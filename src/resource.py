# coding=utf-8
import logging

from .default_error_responses import \
    NotImplementedResponse, \
    InternalServerErrorResponse
from .errors import UserDefinedApiException
from django.conf import settings

log = logging.getLogger(__name__)


class Resource(object):

    def __init__(self):
        super(Resource, self).__init__()

    def create_element(self, request, *args, **kwargs):
        """

        :param request:
        :type request: django.http.HttpRequest
        :return:
        :rtype: django.http.HttpResponse
        """
        raise NotImplementedError()

    def create_list(self, request, *args, **kwargs):
        """

        :param request:
        :type request: django.http.HttpRequest
        :return:
        :rtype: django.http.HttpResponse
        """
        raise NotImplementedError()

    def read_list(self, request, *args, **kwargs):
        """

        :param request:
        :type request: django.http.HttpRequest
        :return:
        :rtype: django.http.HttpResponse
        """
        raise NotImplementedError()

    def read_element(self, request, *args, **kwargs):
        """

        :param request:
        :type request: django.http.HttpRequest
        :return:
        :rtype: django.http.HttpResponse
        """
        raise NotImplementedError()

    def update_partial_element(self, request, *args, **kwargs):
        raise NotImplementedError()

    def update_partial_list(self, request, *args, **kwargs):
        """

        :param request:
        :type request: django.http.HttpRequest
        :return:
        :rtype: django.http.HttpResponse
        """
        raise NotImplementedError()

    def update_element(self, request, *args, **kwargs):
        """

        :param request:
        :type request: django.http.HttpRequest
        :return:
        :rtype: django.http.HttpResponse
        """
        raise NotImplementedError()

    def update(self, request, *args, **kwargs):
        """

        :param request:
        :type request: django.http.HttpRequest
        :return:
        :rtype: django.http.HttpResponse
        """
        raise NotImplementedError()

    def delete(self, request, *args, **kwargs):
        """

        :param request:
        :type request: django.http.HttpRequest
        :return:
        :rtype: django.http.HttpResponse
        """
        raise NotImplementedError()

    def __call__(self, request, identity=None, *args, **kwargs):
        def default(*args, **kwargs):
            raise NotImplementedError()

        methods = {
            'get_element': self.read_element,
            'get_list': self.read_list,

            'put_element': self.update_element,
            'put_list': self.update,

            'delete_element': self.delete,
            'delete_list': self.delete,

            'post_element': self.create_element,
            'post_list': self.create_list,

            'patch_element': self.update_partial_element,
            'patch_list': self.update_partial_list,
        }
        request_method = request.method.lower()
        if identity:
            kwargs['identity'] = identity
            dispatch_key = '{}_element'.format(request_method)
        else:
            dispatch_key = '{}_list'.format(request_method)

        method = methods.get(dispatch_key, default)
        try:
            result = method(request, *args, **kwargs)
            return result
        except UserDefinedApiException as e:
            return e.response
        except NotImplementedError:
            return NotImplementedResponse(
                resource=getattr(self, 'name', request.path),
                method=dispatch_key
            )
        except Exception as e:
            if settings.DEBUG:
                raise
            if getattr(settings, 'RUN_TEST', False) is True:
                # Чтобы в случае упавших тестов было видно стектрейс
                raise
            log.exception(e.message, extra={
                'request': request,
            })
            return InternalServerErrorResponse()
