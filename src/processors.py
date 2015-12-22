class Processor(object):

    def __call__(self, context):
        return context


class ListProcessor(Processor):
    def __init__(self, rules):
        super(ListProcessor, self).__init__()
        self.rules = rules

    def __call__(self, context):
        res = []
        for item in context:
            res.append(self.rules(item))
        return res


class DistinctListProcessor(ListProcessor):
    def __call__(self, context):
        result = super(DistinctListProcessor, self).__call__(context)
        return set(result)


class RelatedProcessor(ListProcessor):
    def __call__(self, context):
        if hasattr(context, 'all'):
            return super(RelatedProcessor, self).__call__(context.all())
        else:
            return super(RelatedProcessor, self).__call__(context)


class DistinctRelatedProcessor(DistinctListProcessor):
    def __call__(self, context):
        if hasattr(context, 'all'):
            return super(DistinctRelatedProcessor, self).__call__(context.all())
        else:
            return super(DistinctRelatedProcessor, self).__call__(context)