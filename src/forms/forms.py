# coding=utf-8
from collections import defaultdict
import copy

from django.utils.encoding import python_2_unicode_compatible
from django.utils import six
from django.utils.datastructures import SortedDict

from . import fields
from . import exceptions


def get_declared_fields(bases, attrs, with_base_fields=True):
    """
    Create a list of form field instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases'). This is used by both the
    Form and ModelForm metclasses.

    If 'with_base_fields' is True, all fields from the bases are used.
    Otherwise, only fields in the 'declared_fields' attribute on the bases are
    used. The distinction is useful in ModelForm subclassing.
    Also integrates any additional media definitions
    """
    field_list = []
    for field_name, obj in list(six.iteritems(attrs)):
        if isinstance(obj, fields.Field):
            field_list.append((field_name, attrs.pop(field_name)))

    field_list.sort(key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                field_list = list(six.iteritems(base.base_fields)) + field_list
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_fields'):
                field_list = list(six.iteritems(base.declared_fields)) + field_list

    return SortedDict(field_list)


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = get_declared_fields(bases, attrs)
        return super(DeclarativeFieldsMetaclass, cls).\
            __new__(cls, name, bases, attrs)


@python_2_unicode_compatible
class BoundField(object):
    def __init__(self, form, field, name):
        self.form = form
        self.field = field
        self.name = name
        self.help_text = field.help_text or ''

    def _errors(self):
        """
        Returns an ErrorList for this field. Returns an empty ErrorList
        if there are none.
        """
        return self.form.errors.get(self.name, [])
    errors = property(_errors)

    def value(self):
        """
        Returns the value for this BoundField, using the initial value if
        the form is not bound or the data otherwise.
        """
        if self.name in self.form.data:
            data = self.form.data[self.name]
        else:
            data = self.form.initial.get(self.name, self.field.initial)

        return self.field.prepare_value(data)


@python_2_unicode_compatible
class BaseForm(object):
    # This is the main implementation of all the Form logic. Note that this
    # class is different than Form. See the comments by the Form class for more
    # information. Any improvements to the form API should be made to *this*
    # class, not to the Form class.
    def __init__(self, data=None, files=None, empty_permitted=False):
        self.is_bound = data is not None or files is not None
        self.data = data or {}
        self.files = files or {}
        self.empty_permitted = empty_permitted
        self._exceptions = None
        self._errors = None
        self._changed_data = None

        # The base_fields class attribute is the *class-wide* definition of
        # fields. Because a particular *instance* of the class might want to
        # alter self.fields, we create self.fields here by copying base_fields.
        # Instances should always modify self.fields; they should not modify
        # self.base_fields.
        self.fields = copy.deepcopy(self.base_fields)

    def has_bound_fields(self):
        field_names = set(self.fields.keys())
        data_names = set(self.data.keys())
        return bool(field_names.intersection(data_names))

    def __iter__(self):
        for name in self.fields:
            yield self[name]

    def __getitem__(self, name):
        "Returns a BoundField with the given name."
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError('Key %r not found in Form' % name)
        return BoundField(self, field, name)

    def _get_errors(self):
        "Returns an ErrorDict for the data provided for the form"
        if self._errors is None:
            self.full_clean()
        return self._errors
    errors = property(_get_errors)

    def is_valid(self):
        """
        Returns True if the form has no errors. Otherwise, False. If errors are
        being ignored, returns False.
        """
        return self.is_bound and not bool(self.errors)

    def _raw_value(self, fieldname):
        """
        Returns the raw_value for a particular field name. This is just a
        convenient wrapper around widget.value_from_datadict.
        """
        field = self.fields[fieldname]
        return field.get_bound_value()

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self.cleaned_data.
        """
        self._errors = defaultdict(list)
        self.cleaned_data = {}

        self._clean_fields()
        self._clean_form()
        self._post_clean()

    def add_field_error(self, name, e):
        self._errors[name].append(e)

    def _process_clean_error(self, name, e):
        self.add_field_error(name, e)

        if name in self.cleaned_data:
            del self.cleaned_data[name]

    def _clean_field(self, field, name):
        value = self.data.get(name, field.initial)
        try:
            value = field.clean(value)
            self.cleaned_data[name] = value
            if hasattr(self, 'clean_%s' % name):
                value = getattr(self, 'clean_%s' % name)()
                self.cleaned_data[name] = value
        except exceptions.ValidationError as e:
            self._process_clean_error(name, e)
        except exceptions.MultipleValidationError as e:
            for exception in e.errors:
                self._process_clean_error(name, exception)

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            self._clean_field(field, name)

    def _clean_form(self):
        # Не нужно запускать clean формы, т.к она полагается на
        # то что все поля не содержат ошибок сами по себе
        if self._errors:
            return

        try:
            self.cleaned_data = self.clean()
        except exceptions.ValidationError as e:
            self._errors['__all__'].append(e)

    def _post_clean(self):
        """
        An internal hook for performing additional cleaning after form cleaning
        is complete. Used for model validation in model forms.
        """
        pass

    def clean(self):
        """
        Hook for doing any extra form-wide cleaning after Field.clean() been
        called on every field. Any ValidationError raised by this method will
        not be associated with a particular field; it will have a special-case
        association with the field named '__all__'.
        """
        return self.cleaned_data


class Form(six.with_metaclass(DeclarativeFieldsMetaclass, BaseForm)):
    "A collection of Fields, plus their associated data."

    def add_field_error(self, name, e):
        super(Form, self).add_field_error(name, e)


class PartialSaveForm(Form):
    def __init__(self, *args, **kwargs):
        super(PartialSaveForm, self).__init__(*args, **kwargs)
        self.__required_fields = None
        self.fields_to_check = self.data.keys()

    def _clean_fields(self):
        for name, field in self.fields.items():
            if name not in self.fields_to_check:
                continue
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            self._clean_field(field, name)

    def _process_clean_error(self, name, e):
        if self.__required_fields and name in self.__required_fields:
            self.add_field_error(name, e)

        if name in self.cleaned_data:
            del self.cleaned_data[name]
