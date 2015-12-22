import logging
import operator as op
import uuid

from collections import defaultdict
from decimal import Decimal

from ..processors import RelatedProcessor, \
    DistinctRelatedProcessor

logger = logging.getLogger(__name__)


class AccessorsFactory(object):
    __getters = defaultdict(dict)

    @classmethod
    def make_getter(cls, path, key, obj, namespace='_'):
        storage = cls.__getters[namespace]
        path += '_getter'

        if path in storage:
            return storage[path]

        if isinstance(obj, dict):
            getter = op.itemgetter(key)
        else:
            getter = op.attrgetter(key)

        storage[path] = getter
        cls.__getters[namespace] = storage
        return getter

    @classmethod
    def resolve_steps(cls, obj, steps, ns=None, force_create=False):
        current_path = ''
        res = obj
        for step in steps:
            current_path += step
            try:
                getter = AccessorsFactory.make_getter(
                    current_path, step, res, namespace=ns
                )
                res = getter(res)
            except (KeyError, AttributeError):
                if isinstance(res, dict) and force_create:
                    res[step] = {}
                    res = res[step]
                else:
                    raise
        return res

    @classmethod
    def get_by_path(cls, obj, path, ns=None):
        if not path:
            return obj

        steps = path.split('.')
        res = cls.resolve_steps(obj, steps, ns)
        return res

    @classmethod
    def set_by_path(cls, obj, path, value, ns=None):
        if not path:
            return obj

        steps = path.split('.')
        context = cls.resolve_steps(
            obj, steps[:-1], ns=ns, force_create=True
        )

        if isinstance(context, dict):
            context[steps[-1]] = value

        return obj

def field_documentation(rtype=None, is_null=None, choices=None, complex_preparer=None):
    def decorator(func):

        if decorator.rtype is not None:
            func.documentation_return_type = rtype

        is_null = False
        if decorator.is_null is None:
            is_null = getattr(func, 'documentation_is_null', False)

        func.documentation_is_null = is_null
        func.documentation_choices = choices
        func.documentation_complex_preparer = complex_preparer
        return func

    decorator.is_null = is_null
    decorator.rtype = rtype
    return decorator


class Field(object):
    def __init__(self, src=None, trg=None, context=None, default=None, **kwargs):
        self.default = default
        self.context = context
        self.src = src
        self.trg = trg
        self.uuid = unicode(uuid.uuid4())

    def contribute_to_class(self, name, new_class):

        if hasattr(new_class, '_rules'):
            rules = new_class._rules or []
        else:
            rules = []

        if self.src == 'self':
            self.src = None
        elif self.src is None:
            self.src = name

        if not self.trg:
            self.trg = name

        rules.append(
            self
        )
        new_class._rules = rules

    def get_value(self, value):
        return value

    def set_value(self, res, value):
        AccessorsFactory.set_by_path(
            res,
            self.trg,
            value,
            ns=self.uuid
        )

    def get_value_from_context_and_set_to_result(self, context_object, res):
        local_context = AccessorsFactory.get_by_path(
            context_object,
            self.context,
            ns=self.uuid,
        )

        value_to_process = AccessorsFactory.get_by_path(
            local_context,
            self.src,
            ns=self.uuid,
        )

        if hasattr(value_to_process, '__call__'):
            value_to_process = value_to_process()

        try:
            value = self.get_value(value_to_process)
        except ImmediateResultException as e:
            value = e.result
        except Exception:
            logger.debug(
                '{}, {}, {}, {}'.format(
                    self.context,
                    self.src,
                    self.trg,
                    local_context.keys() if isinstance(local_context, dict) else local_context
                )
            )
            raise

        if value is None and self.default is not None:
            value = self.default

        self.set_value(
            res, value
        )


class ImmediateResultException(Exception):
    def __init__(self, result, *args, **kwargs):
        super(ImmediateResultException, self).__init__(*args, **kwargs)
        self.result = result


@field_documentation(is_null=True)
class NullField(Field):
    def __init__(self, src=None, trg=None, processor=None, context=None,
                 default=None):
        super(NullField, self).__init__(src, trg, processor, context)
        self.default = default

    def get_value(self, context):
        if context is None:
            raise ImmediateResultException(
                result=self.default
            )
        return context


@field_documentation(rtype='int')
class IntField(Field):
    def get_value(self, context):
        return int(context)


@field_documentation(rtype='str')
class CharField(Field):
    def get_value(self, context):
        try:
            return unicode(context)
        except UnicodeDecodeError:
            return unicode(context.decode('utf-8'))


@field_documentation(rtype='str')
class DjangoDisplayPropertyField(Field):
    def get_value(self, context):
        attr = 'get_{}_display'.format(self.trg)
        return getattr(context, attr)()


@field_documentation(rtype='complex')
class RelatedInstanceField(Field):
    def __init__(self, src=None, trg=None, post_processor=None, context=None,
                 serializer=None):
        super(RelatedInstanceField, self).__init__(
            src, trg, context
        )
        self.serializer = serializer

    def get_value(self, context):
        if context is None:
            raise ImmediateResultException(result=None)
        return self.serializer(context)


@field_documentation(rtype='complex')
class RelatedIterableField(Field):
    def __init__(self, src=None, trg=None, post_processor=None, context=None,
                 serializer=None, default=None, distinct=False):
        super(RelatedIterableField, self).__init__(
            src, trg, context
        )
        self.serializer = serializer
        self.distinct = distinct

    def get_value(self, context):
        if context is None:
            raise ImmediateResultException(result=None)
        if self.distinct:
            return DistinctRelatedProcessor(self.serializer)(context)
        else:
            return RelatedProcessor(self.serializer)(context)


@field_documentation(rtype='decimal')
class DecimalField(Field):
    def get_value(self, context):
        return Decimal(context)


@field_documentation(rtype='decimal')
class NullDecimalField(NullField):
    def get_value(self, context):
        context = super(NullDecimalField, self).get_value(context)
        return Decimal(context)


@field_documentation(rtype='str')
class NullCharField(NullField):
    def get_value(self, context):
        context = super(NullCharField, self).get_value(context)
        try:
            return unicode(context)
        except UnicodeDecodeError:
            return unicode(context.decode('utf-8'))


@field_documentation(rtype='int')
class NullIntField(NullField):
    def get_value(self, context):
        context = super(NullIntField, self).get_value(context)
        return int(context)


@field_documentation(rtype='bool')
class NullBooleanField(NullField):
    def get_value(self, context):
        context = super(NullBooleanField, self).get_value(context)
        return bool(context)


@field_documentation(rtype='bool')
class BooleanField(Field):
    def get_value(self, context):
        return bool(context)


class ValueMockField(Field):
    def __init__(self, val, src=None, trg=None, processor=None, context=None):
        super(ValueMockField, self).__init__(src, trg, processor, context)
        self.val = val

    def get_value(self, context):
        return self.val


@field_documentation(rtype='datetime')
class NullDateTimeField(NullField):
    def get_value(self, context):
        context = super(NullDateTimeField, self).get_value(context)
        return self.fmt.format(context)

    def __init__(self, src=None, trg=None, fmt=u'{}', context=None):
        super(NullDateTimeField, self).__init__(src, trg, None, context)
        self.fmt = fmt


@field_documentation(rtype='datetime')
class DateTimeField(Field):
    def get_value(self, context):
        return self.fmt.format(context)

    def __init__(self, src=None, trg=None, fmt=u'{}', context=None):
        super(DateTimeField, self).__init__(src, trg, None, context)
        self.fmt = fmt


@field_documentation(rtype='datetime')
class TimeField(Field):
    def get_value(self, context):
        return self.fmt.format(context)

    def __init__(self, src=None, trg=None, fmt=u'{:%H:%M}', context=None):
        super(TimeField, self).__init__(src, trg, None, context)
        self.fmt = fmt

@field_documentation(rtype='datetime')
class DateField(Field):
    def get_value(self, context):
        return self.fmt.format(context)

    def __init__(self, src=None, trg=None, fmt=u'{:%Y-%m-%d}', context=None):
        super(DateField, self).__init__(src, trg, None, context)
        self.fmt = fmt

@field_documentation(rtype='float')
class FloatField(Field):
    def get_value(self, context):
        return float(context)


@field_documentation(rtype='float')
class NullFloatField(NullField):
    def get_value(self, context):
        context = super(NullFloatField, self).get_value(context)
        return float(context)


@field_documentation(rtype='str')
class NullDjangoDisplayPropertyField(NullField):
    def get_value(self, context):
        attr = 'get_{}_display'.format(self.trg)
        return getattr(context, attr)()


@field_documentation(rtype='array_float')
class FloatArrayField(Field):
    def get_value(self, context):
        if context is None:
            return []

        return map(float, context)
