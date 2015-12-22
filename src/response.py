import decimal
import datetime
import json

from django.http import HttpResponse
from django.utils.functional import curry

from .errors import UserDefinedApiException


class ErrorAlreadyRegisteredCode(Exception):
    def __init__(self, code):
        self.message = u"{} is already registered".format(
            code
        )
        super(ErrorAlreadyRegisteredCode, self).__init__()


class UnknownErrorCode(Exception):
    def __init__(self, code):
        self.message = u"Unknown error code: {}".format(
            code
        )
        super(UnknownErrorCode, self).__init__()


class ErrorCodeRegistry(object):
    __registry = {}

    @classmethod
    def add(cls, code, message, status_code):
        if code in cls.__registry:
            raise ErrorAlreadyRegisteredCode(code)
        cls.__registry[code] = (message, status_code)

    @classmethod
    def get(cls, code):
        if code not in cls.__registry:
            raise UnknownErrorCode(code)

        return cls.__registry.get(code)


def default_callback(value):
    types = {
        decimal.Decimal: lambda v: float('{:0.2f}'.format(v)),
        datetime.datetime: lambda v: '{:%Y-%m-%dT%H-%M-%S}'.format(v),
        datetime.date: lambda v: '{:%Y-%m-%d}'.format(v),
        datetime.time: lambda v: '{:%H:%M:%S}'.format(v),
        set: lambda v: list(v),
    }
    return types.get(type(value), lambda v: None)(value)


class JsonResponse(HttpResponse):
    def __init__(self, content=None, mimetype=None, status=None):
        if content is None:
            content = []

        if not isinstance(content, basestring):
            content = json.dumps(content, default=default_callback)

        super(JsonResponse, self).__init__(
            content,
            mimetype,
            status,
            'application/json'
        )


class JsonResponseWithMetadata(JsonResponse):
    def __init__(self, objects=None, meta=None):
        default_meta = {
            'page': 1,
            'count': len(objects),
            'limit': len(objects)
        }
        content = {
            'objects': [] if objects is None else objects,
            'meta': meta or default_meta
        }
        super(JsonResponseWithMetadata, self).__init__(content)


class ErrorResponse(JsonResponse):
    def __init__(self, code, **kwargs):
        message, status = ErrorCodeRegistry.get(code)

        errors = []
        if 'errors' in kwargs:
            for error in kwargs['errors']:
                errors.append(
                    {
                        'message': message.format(**error),
                        'meta': error
                    }
                )
        else:
            errors.append(
                {
                    'message': message.format(**kwargs),
                    'meta': kwargs
                }
            )

        content = {
            "errors": errors,
            "code": code
        }
        super(ErrorResponse, self).__init__(content=content, status=status)

    @classmethod
    def build_new(cls, code, message, status):
        ErrorCodeRegistry.add(code, message, status)
        return curry(ErrorResponse, code=code)

    def throw(self):
        raise UserDefinedApiException(response=self)
