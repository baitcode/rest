# rest

Classes, functions and decorators for building REST APIs on Django. Written in
2015 for Python 2 and the Django versions of that time.

## What's inside

| Module | What it does |
| --- | --- |
| `api.py` | `Api` registers resources under a version and generates list and element URL patterns |
| `resource.py` | `Resource` base class: dispatches each HTTP method to a list or element handler (`read_list`, `read_element`, `create_element`, `update_element`, `delete`, ...) |
| `forms/` | Input validation without Django forms: typed fields (char, integer, decimal, date, choice, array, dict, ...) and validators (`Required`, `MinMax`, `MinMaxLength`, `Regexp`) |
| `params.py` | Request parameter checks such as `require(name).at(location)` |
| `preparers/` | Declarative serialisers that turn objects into response dictionaries |
| `response.py` | `JsonResponse`, `ErrorResponse` and an error code registry |
| `docs.py` | `DocumentationApi`: serves the response format of each resource, derived from its preparer |

## Install

```sh
python setup.py install
```

The package installs as `rest` and depends on `Django` and `six`.

## Tests

`src/tests/test_forms.py` covers the forms module. The tests are Django test
cases, so they need to run inside a Django project.

## Status

Not maintained. The code uses Python 2 syntax and Django APIs that have since
been removed (`django.conf.urls.patterns`).
