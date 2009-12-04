# -*- coding: utf-8 -*-
from django.contrib.admin.filterspecs import FilterSpec

FilterSpec.register_first = classmethod(lambda cls, test, factory: cls.filter_specs.insert(0, (test, factory)))

class EmptyStringFilterSpec(FilterSpec):
    """
    class Song(models.Model):
        accords = models.TextField(u'Аккорды', blank=True)
        translation = models.TextField(u'Перевод песни', blank=True)
    
        accords.test_null_filter = True
        translation.test_null_filter = True
    """
    
    def __init__(self, f, request, params, model, model_admin):
        super(EmptyStringFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_kwarg = '%s__exact' % f.name
        self.lookup_kwarg2 = '%s__gt' % f.name
        self.lookup_kwarg3 = '%s__isnull' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_val2 = request.GET.get(self.lookup_kwarg2, None)

    def title(self):
        return u"наличие поля '%s'" % self.field.verbose_name

    def choices(self, cl):
        yield {'selected': self.lookup_val2 is None and self.lookup_val is None,
               'query_string': cl.get_query_string({}, [self.lookup_kwarg2, self.lookup_kwarg, self.lookup_kwarg3]),
               'display': u'Все'}
        yield {'selected': self.lookup_val2 == '' and self.lookup_val is None,
               'query_string': cl.get_query_string({self.lookup_kwarg2: ''}, [self.lookup_kwarg, self.lookup_kwarg3]),
               'display': u'Имеется'}
        yield {'selected': self.lookup_val == '' and self.lookup_val2 is None,
               'query_string': cl.get_query_string({self.lookup_kwarg: ''}, [self.lookup_kwarg2, self.lookup_kwarg3]),
               'display': u'Отсутствует'}

FilterSpec.register_first(lambda f: hasattr(f, 'test_null_filter'), EmptyStringFilterSpec)