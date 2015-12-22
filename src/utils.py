import functools
from django.db import models

import default_error_responses


def json_view_login_required(func):
    @functools.wraps(func)
    def wrapper(resource, request, *args, **kwargs):
        user = request.user
        if not user or not user.is_authenticated():
            return default_error_responses.UnauthenticatedResponse(
                resource=request.path
            )

        return func(
            resource, request, *args, **kwargs
        )

    return wrapper


def json_view_perm_required(perm):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(resource, request, *args, **kwargs):
            user = request.user
            if not user:
                return default_error_responses.UnauthenticatedResponse(
                    resource=request.path
                )

            if not user.has_perm(perm):
                return default_error_responses.UnauthorizedResponse(
                    resource=request.path
                )

            return func(
                resource, request, *args, **kwargs
            )

        return wrapper

    return decorator


def json_view_api_key_authentication(api_key_model, user_fk,
                                     request_username_field,
                                     request_api_key_field,
                                     username_field,
                                     api_key_field):
    assert issubclass(api_key_model, models.Model)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(resource, request, *args, **kwargs):
            username = request.REQUEST.get(request_username_field)
            api_key = request.REQUEST.get(request_api_key_field)
            if not all((username, api_key)):
                return default_error_responses.UnauthenticatedResponse(
                    resource=request.path
                )
            fk_username_field = '{user_fk}__{username_field}'.format(
                user_fk=user_fk,
                username_field=username_field
            )
            lookup_dict = {
                fk_username_field: username,
                api_key_field: api_key,
            }
            try:
                api_key_instance = api_key_model.objects.select_related(user_fk).get(**lookup_dict)
            except (api_key_model.DoesNotExist, api_key_model.MultipleObjectsReturned):
                return default_error_responses.UnauthenticatedResponse(
                    resource=request.path
                )
            setattr(request, 'user', getattr(api_key_instance, user_fk))

            return func(resource, request, *args, **kwargs)

        return wrapper

    return decorator



def json_view_token_required(token):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(resource, request, *args, **kwargs):
            received_token = request.GET.get('token', None)
            if not received_token == token:
                return default_error_responses.UnauthenticatedResponse(
                    resource=request.path
                )

            return func(
                resource, request, *args, **kwargs
            )

        return wrapper

    return decorator
