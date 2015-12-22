from django.conf import settings
from . import validators

DEFAULT_AUTOHOOK_VALIDATORS = [
    validators.Required,
    validators.MinMaxLength,
    validators.MinMax,
    validators.Regexp
]


AUTOHOOK_VALIDATORS = getattr(settings, 'AUTOHOOK_VALIDATORS', []) + \
                      DEFAULT_AUTOHOOK_VALIDATORS