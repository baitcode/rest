import json
import logging
import default_error_responses


log = logging.getLogger(__name__)

always_true = lambda request: True

request_body = lambda r: json.loads(r.body)


class check(object):
    __dict__ = ('name', 'location', 'condition', 'check')

    def get_data(self, request):
        res = {}
        if isinstance(self.location, basestring):
            res = getattr(request, self.location.upper())
        elif callable(self.location):
            res = self.location(request)
        return res

    def __init__(self):
        super(check, self).__init__()
        self.location = 'GET'
        self.name = None
        self.condition = always_true
        self.check = always_true

    def at(self, location):
        self.location = location
        return self

    def when(self, condition):
        self.condition = condition
        return self

    def __call__(self, request):
        if self.condition:
            return self.check(request)
        return True

    def error_message(self):
        return u''

    def value(self, request):
        return None


class require(check):

    def __check(self, request):
        return self.name in self.get_data(request)

    def __init__(self, name, error_response=None):
        super(require, self).__init__()
        self.name = name
        self.check = self.__check
        self.error_response = error_response or \
            default_error_responses.ParameterRequiredResponse

    def error(self):
        self.error_response(
            name=self.name,
            location=self.location
        ).throw()

    def value(self, request):
        return getattr(request, self.location)[self.name]


class pass_through_form(check):

    def __check(self, request):
        data = self.get_data(request)
        form = self.form(data=data)

        if form.is_valid():
            self.__value = form.cleaned_data
            return True
        else:
            self.__errors = form.errors
            return False

    def value(self, request):
        return self.__value

    def error(self):
        to_render = []
        for fieldname, errors in self.__errors.items():
            for error in errors:
                to_render.append({
                    'parameter': fieldname,
                    'message': error.message.format(**error.params),
                    'code': error.code,
                    'params': error.params
                })

        default_error_responses.RequestValidationFailedResponse(
            errors=to_render
        ).throw()

    def __call__(self, request):
        self.__value = None
        self.__errors = None
        return super(pass_through_form, self).__call__(request)

    def __init__(self, form, error_response=None, location=None):
        super(pass_through_form, self).__init__()
        self.location = location or self.location
        self.check = self.__check
        self.name = 'data'
        self.form = form
        self.error_response = error_response or \
            default_error_responses.RequestValidationFailedResponse


class pass_through_forms(check):

    def __check(self, request):
        data = self.get_data(request)
        valid_data = {}

        has_errors = False
        for formClass in self.forms:
            form = formClass(data=data)

            if not form.has_bound_fields():
                continue

            if form.is_valid():
                valid_data.update(form.cleaned_data)
            else:
                has_errors = True
                if self.__errors is None:
                    self.__errors = form.errors
                else:
                    self.__errors.update(form.errors)
        self.__value = valid_data
        return not has_errors

    def value(self, request):
        return self.__value

    def error(self):
        to_render = []
        for fieldname, errors in self.__errors.items():
            for error in errors:
                to_render.append({
                    'parameter': fieldname,
                    'message': error.message.format(**error.params),
                    'code': error.code,
                    'params': error.params
                })

        default_error_responses.RequestValidationFailedResponse(
            errors=to_render
        ).throw()

    def __call__(self, request):
        self.__value = None
        self.__errors = None
        return super(pass_through_forms, self).__call__(request)

    def __init__(self, forms, location=None):
        super(pass_through_forms, self).__init__()
        self.location = location or self.location
        self.check = self.__check
        self.name = 'data'
        self.forms = forms


class pass_list_through_form(check):

    def __check(self, request):
        datas = self.get_data(request)
        for data in datas:
            form = self.form(data=data)

            if form.is_valid():
                if self.__value is None:
                    self.__value = [
                        form.cleaned_data
                    ]
                else:
                    self.__value.append(form.cleaned_data)
            else:
                self.__errors = form.errors
                return False
        return True

    def value(self, request):
        return self.__value

    def error(self):
        to_render = []
        for fieldname, errors in self.__errors.items():
            for error in errors:
                to_render.append({
                    'parameter': fieldname,
                    'message': error.message.format(**error.params),
                    'code': error.code,
                    'params': error.params
                })

        default_error_responses.RequestValidationFailedResponse(
            errors=to_render
        ).throw()

    def __call__(self, request):
        self.__value = None
        self.__errors = None
        return super(pass_list_through_form, self).__call__(request)

    def __init__(self, form, location=None):
        super(pass_list_through_form, self).__init__()
        self.location = location or self.location
        self.check = self.__check
        self.name = 'data'
        self.form = form


def check_request(request, rules=None):
    results = {}
    if not rules:
        return results

    for rule in rules:
        if not rule(request):
            return rule.error()
        else:
            if rule.name:
                results[rule.name] = rule.value(request)

    return results