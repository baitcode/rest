from . import exceptions
import re


class Validator(object):
    def validate(self, value, field):
        return True


class Required(Validator):
    hooks = {
        'required': 'is_required'
    }

    def __init__(self, is_required=None):
        super(Required, self).__init__()
        self.is_required = is_required

    def validate(self, value, field):
        if self.is_required and value is None:
            raise exceptions.ValidationError(
                message="Parameter is required",
                code=exceptions.VALIDATION_REQUIRED
            )

        return super(Required, self).validate(value, field)


class MinMax(Validator):
    hooks = {
        'min_value': 'min',
        'max_value': 'max'
    }

    def __init__(self, min=None, max=None):
        super(MinMax, self).__init__()
        self.min = min
        self.max = max

    def validate(self, value, field):
        if value is None:
            return True

        value = field.to_python(value)

        if value is None:
            return True

        if self.min is not None and value < self.min:
            raise exceptions.ValidationError(
                message="Value should be greater than {min}",
                code=exceptions.VALIDATION_VALUE_SHOULD_BE_GREATER,
                min=self.min
            )

        if self.max is not None and value > self.max:
            raise exceptions.ValidationError(
                message="Value should be less than {max}",
                code=exceptions.VALIDATION_VALUE_SHOULD_BE_LESS,
                max=self.max
            )

        return super(MinMax, self).validate(value, field)


class MinMaxLength(Validator):
    hooks = {
        'min_length': 'min',
        'max_length': 'max'
    }

    def __init__(self, min=None, max=None):
        super(MinMaxLength, self).__init__()
        self.min = min
        self.max = max

    def validate(self, value, field):
        if value is None:
            return True

        value = field.to_python(value)

        if value is None:
            return True

        if self.min is not None and len(value) < self.min:
            raise exceptions.ValidationError(
                message="Value length should be greater than {min}",
                code=exceptions.VALIDATION_VALUE_LENGTH_SHOULD_BE_GREATER,
                min=self.min
            )

        if self.max is not None and len(value) > self.max:
            raise exceptions.ValidationError(
                message="Value length should be less than {max}",
                code=exceptions.VALIDATION_VALUE_LENGTH_SHOULD_BE_LESS,
                max=self.max
            )

        return super(MinMaxLength, self).validate(value, field)


class Regexp(Validator):
    hooks = {
        'pattern': 'pattern'
    }

    def __init__(self, pattern=None):
        super(Regexp, self).__init__()
        self.pattern = pattern
        self.regex = re.compile(pattern)

    def validate(self, value, field):
        if value is None:
            return True

        value = field.to_python(value)

        if value is None:
            return True

        if self.regex is not None and not self.regex.match(unicode(value)):
            raise exceptions.ValidationError(
                message="Value didn't match {pattern}",
                code=exceptions.VALIDATION_REGEXP,
                pattern=self.pattern
            )

        return super(Regexp, self).validate(value, field)
