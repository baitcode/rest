# coding=utf-8

"""
Format candidate:

{
  <key>: {
    type: <type>,
    restrictions: { -- optional
      format: <regex>,
      choices: <list_of_choices>,
      <restriction_name>: <value>
    }
  },
}

"""
from . import api, response
from django.conf import urls


def convert_preparer_into_response_format(preparer):
    response = {}
    for rule in preparer._rules:
        slf = rule.processor.im_self
        rtype = getattr(slf, 'documentation_return_type', 'unknown')

        nested = None
        if rtype == 'complex':
            nested = convert_preparer_into_response_format(slf.serializer)

        is_null = getattr(slf, 'documentation_is_null', 'unknown')
        format = getattr(slf, 'fmt', None)
        choices = getattr(slf, 'documentation_choices', None)
        response[rule.trg] = {
            "type": rtype,
            "is_null": is_null,
        }
        if format:
            response[rule.trg]['format'] = format
        if nested:
            response[rule.trg]['nested'] = nested
        if choices:
            response[rule.trg]['choices'] = choices
    return response


class DocumentationMixin(object):

    def get_response_serializer(self):
        raise NotImplemented()

    def show_documentation(self, request):
        return response.JsonResponse(
            self.get_response_serializer()
        )


class DocumentationApi(api.BaseApi):
    list_url_tmpl = r'^{version}/docs/{name}/?$'

    def get_resource_urls(self, name, resource):
        if not isinstance(resource, DocumentationMixin):
            return []

        list_url_regex = self.list_url_tmpl.format(
            version=self.version,
            name=name
        )
        resource_urls = (
            urls.url(list_url_regex, resource.show_documentation),
        )
        return resource_urls