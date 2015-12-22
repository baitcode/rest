from django.conf import urls


class BaseApi(object):

    def __init__(self, version):
        super(BaseApi, self).__init__()
        self.version = version
        self._resources = {}

    def register(self, **resources):
        self._resources.update(resources)
        return self

    def get_resource_urls(self, name, resource):
        pass

    @property
    def urls(self):
        url_list = urls.patterns('')
        for name, resource in self._resources.items():
            resource_urls = self.get_resource_urls(name, resource)
            url_list += resource_urls
        return url_list


class Api(BaseApi):
    list_url_tmpl = r'^{version}/{name}/?$'
    element_url_tmpl = r'^{version}/{name}/(?P<identity>[\w\d-]+?)/?$'
    list_name_tmpl = 'api_{version}_{name}_list'
    element_name_tmpl = 'api_{version}_{name}_element'

    def get_resource_urls(self, name, resource):
        url_list = urls.patterns('')
        for name, resource in self._resources.items():
            list_url_regex = self.list_url_tmpl.format(
                version=self.version,
                name=name
            )
            element_url_regex = self.element_url_tmpl.format(
                version=self.version,
                name=name
            )
            list_name = self.list_name_tmpl.format(
                version=self.version,
                name=name
            )
            element_name = self.element_name_tmpl.format(
                version=self.version,
                name=name,
            )
            url_list += (
                urls.url(list_url_regex, resource, name=list_name),
                urls.url(element_url_regex, resource, name=element_name),
            )
        return url_list

