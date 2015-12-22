from django.core import exceptions


VALIDATION_REQUIRED = 'is_required'
VALIDATION_INVALID_VALUE = 'is_invalid'

VALIDATION_REGEXP = 'is_invalid_regex'

VALIDATION_VALUE_SHOULD_BE_GREATER = 'value_is_small'
VALIDATION_VALUE_SHOULD_BE_LESS = 'value_is_big'

VALIDATION_VALUE_LENGTH_SHOULD_BE_GREATER = 'value_length_is_small'
VALIDATION_VALUE_LENGTH_SHOULD_BE_LESS = 'value_length_is_big'

VALIDATION_INVALID_ARRAY_MAX_LENGTH = 'max_length'
VALIDATION_INVALID_ARRAY_MIN_LENGTH = 'min_length'
VALIDATION_INVALID_NOT_ARRAY = 'not_array'
VALIDATION_RELATED_INSTANCE_ARRAY_ERROR = 'related_array_error'
VALIDATION_RELATED_INSTANCE_ERROR = 'related_instance_error'
VALIDATION_RELATED_INSTANCE_NOT_AN_OBJECT = 'not_an_object'
VALIDATION_REQUIRED_FIELD_MISSING = 'required_field_missing'


class ValidationError(Exception):
    def __init__(self, message, code=None, **params):
        super(ValidationError, self).__init__(message)
        self.params = params or {}
        self.code = code


class MultipleValidationError(Exception):
    def __init__(self, errors):
        super(MultipleValidationError, self).__init__()
        self.errors = errors

