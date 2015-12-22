import copy
import decimal
import datetime
from dateutil import parser

from . import exceptions
from . import settings

EMAIL_REGEXP = r'[^@]+@[^@]+\.[^@]+'

FORM_ERROR_KEY = '__all__'

class Field(object):
    default_validators = [] # Default set of validators

    # Tracks each time a Field instance is created. Used to retain order.
    creation_counter = 0

    def __init__(self, initial=None, validators=None, **kwargs):
        self.validators = []

        for validator in settings.AUTOHOOK_VALIDATORS:
            call_options = set(kwargs.keys())
            hooks = validator.hooks
            hook_keys = set(hooks.keys())
            options = hook_keys.intersection(call_options)
            if options:
                validator_options = {}
                for o in options:
                    validator_options[hooks[o]] = kwargs[o]

                self.validators.append(
                    validator(**validator_options)
                )

        self.initial = initial
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1
        self.validators.extend(self.default_validators)
        self.validators.extend(validators or [])

    def prepare_value(self, value):
        return value

    def to_python(self, value):
        return value

    def run_validators(self, value):
        errors = []
        for v in self.validators:
            try:
                v.validate(value, self)
            except exceptions.ValidationError as e:
                errors.append(e)

        if errors:
            raise exceptions.MultipleValidationError(errors)

    def clean(self, value):
        """
        Validates the given value and returns its "cleaned" value as an
        appropriate Python object.

        Raises exceptions.ValidationError for any errors.
        """
        try:
            self.run_validators(value)
            return self.to_python(value)
        except ValueError:
            raise exceptions.ValidationError(
                code=exceptions.VALIDATION_INVALID_VALUE,
                message="Value {value} is invalid",
                value=value
            )

    def bound_data(self, data, initial):
        """
        Return the value that should be shown for this field on render of a
        bound form, given the submitted POST data for the field and the initial
        data, if any.

        For most fields, this will simply be data; FileFields need to handle it
        a bit differently.
        """
        return data

    def get_bound_value(self):
        return self.initial

    def __deepcopy__(self, memo):
        result = copy.copy(self)
        memo[id(self)] = result
        result.validators = self.validators[:]
        return result


class CharField(Field):
    def to_python(self, value):
        if value is None:
            return value

        return unicode(value)


class IntegerField(Field):
    def to_python(self, value):
        if value is None:
            return value

        return int(value)


class DecimalField(Field):

    def __init__(self, *args, **kwargs):
        self.decimal_places = kwargs.pop('decimal_places', 8)
        super(DecimalField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is None:
            return value

        try:
            return decimal.Decimal(value).quantize(decimal.Decimal('.{dp}'.format(
                dp='1' * self.decimal_places,
            )))
        except decimal.DecimalException:
            raise ValueError('invalid value')


class DateField(Field):
    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, basestring) and value:
            value = parser.parse(value)

        if isinstance(value, datetime.datetime):
            value = value.date()

        if not isinstance(value, datetime.date):
            raise exceptions.ValidationError(
                code=exceptions.VALIDATION_INVALID_VALUE,
                message='Value {value} for "{parameter}" is invalid',
            )
        return value


class TimeField(Field):
    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, basestring) and value:
            value = parser.parse(value)

        if isinstance(value, datetime.datetime):
            value = value.time()

        if not isinstance(value, datetime.time):
            raise ValueError()

        return value


class ChoiceField(Field):
    def __init__(self, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self.choices = set(kwargs['choices'])

    def to_python(self, value):
        if value is None:
            return value

        if value not in self.choices:
            raise ValueError('invalid_choice')

        return value


class EmailField(CharField):
    def __init__(self, pattern=EMAIL_REGEXP, *args, **kwargs):
        kwargs['pattern'] = pattern
        super(EmailField, self).__init__(*args, **kwargs)


class FloatField(Field):
    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, (basestring, decimal.Decimal)):
            value = float(value)

        return value


class BooleanField(Field):

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, basestring):
            value = value.lower()
            if value == 'true':
                value = True
            elif value == 'false':
                value = False

        if not isinstance(value, bool):
            raise ValueError('invalid_bool')

        return bool(value)


class InstanceField(Field):

    def to_python(self, value):
        return value


class ArrayField(Field):
    ARRAY_DELIMETER = ','

    def __init__(self, *args, **kwargs):
        super(ArrayField, self).__init__(*args, **kwargs)
        self.separator = kwargs.get('separator', self.ARRAY_DELIMETER)

    def to_python(self, value):
        if value is None:
            return value

        if isinstance(value, basestring):
            if value == '':
                return super(ArrayField, self).to_python([])

            value = value.strip("[").strip("]")\
                .strip("(").strip(")")\
                .split(self.separator)

        if not isinstance(value, list):
            raise ValueError('invalid_list')

        return super(ArrayField, self).to_python(value or [])


class IntArrayField(ArrayField):

    def to_python(self, value):
        value = super(IntArrayField, self).to_python(value)

        if value is None:
            return

        result = []
        for item in value:
            result.append(int(item))

        return result


class CharArrayField(ArrayField):
    def to_python(self, value):
        value = super(CharArrayField, self).to_python(value)
        mapped = []
        for item in value:
            mapped.append(unicode(item))

        return mapped


class DecimalArrayField(ArrayField):

    def __init__(self, *args, **kwargs):
        self.decimal_places = kwargs.pop('decimal_places', 25)
        super(DecimalArrayField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        value = super(DecimalArrayField, self).to_python(value)

        if value is None:
            return

        mapped = []
        for item in value:
            mapped.append(decimal.Decimal(item).quantize(decimal.Decimal('.{dp}'.format(
                dp='1' * self.decimal_places,
            ))))

        return mapped


class DictArrayField(ArrayField):
    def __init__(self, form, *args, **kwargs):
        super(DictArrayField, self).__init__(*args, **kwargs)
        self.form = form

    def to_python(self, value):
        value = super(DictArrayField, self).to_python(value)

        if value is None:
            return value

        result = []
        for item in value:
            if not isinstance(item, dict):
                raise ValueError('not_an_object')

            f = self.form(data=item)
            if not f.is_valid():
                field_name, errors = f.errors.items()[0]
                raise exceptions.ValidationError(
                    u'Error in {field_name} field. {message}'.format(
                        field_name=field_name,
                        message=errors
                    ),
                    code=exceptions.VALIDATION_RELATED_INSTANCE_ARRAY_ERROR
                )
            else:
                result.append(f.cleaned_data)

        return result


class DictField(Field):

    def __init__(self, form=None, *args, **kwargs):
        super(DictField, self).__init__(*args, **kwargs)
        self.form = form

    def to_python(self, value):
        value = super(DictField, self).to_python(value)

        if value is None:
            return value

        if not isinstance(value, dict):
            raise ValueError('not_an_object')

        if not self.form:
            return

        f = self.form(data=value)
        if not f.is_valid():
            field_name, errors = f.errors.items()[0]
            raise exceptions.ValidationError(
                u'Error in {field_name} field. {message}'.format(
                    field_name=field_name,
                    message=errors
                ),
                code=exceptions.VALIDATION_RELATED_INSTANCE_ARRAY_ERROR
            )
        return f.cleaned_data
