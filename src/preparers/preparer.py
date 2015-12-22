# from hotels.api.v3.rest.rules import Rules


class PreparerMetaClass(type):
    def __new__(cls, name, bases, attrs):
        is_preparer = False
        for base in bases:
            if isinstance(base, PreparerMetaClass):
                is_preparer = True

        if not is_preparer:
            return super(PreparerMetaClass, cls).__new__(
                cls, name, bases, attrs
            )

        new_class = super(PreparerMetaClass, cls).__new__(
            cls, name, bases, attrs
        )

        for name, attr in attrs.items():
            if hasattr(attr, 'contribute_to_class'):
                attr.contribute_to_class(name, new_class)

        metadata_class = attrs.get('Meta')

        if metadata_class:
            new_class._meta = metadata_class()
        else:
            new_class._meta = {}

        return new_class


class Preparer(object):
    __dict__ = ('rules', '_rules')
    __metaclass__ = PreparerMetaClass

    _rules = None

    def get_default_context(self):
        context = None
        if hasattr(self._meta, 'default_context'):
            context = self._meta.default_context
        return context

    def apply_context_to_rules(self, context):
        for r in self._rules:
            if not r.context:
                r.context = context

    def __init__(self, context=None):
        super(Preparer, self).__init__()

        assert self._rules

        context = context or self.get_default_context()

        if context:
            self.apply_context_to_rules(context)

        self.rules = self._rules

    def __call__(self, context_object):
        res = {}
        for rule in self.rules:
            rule.get_value_from_context_and_set_to_result(context_object, res)
        return res


