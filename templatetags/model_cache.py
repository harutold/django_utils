#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.template import resolve_variable
from django.core.cache import cache
from django_utils import view_set_cache
from django.utils.encoding import force_unicode
from django.utils.http import urlquote
from django.utils.functional import curry

register = Library()

class CacheNode(Node):
    def __init__(self, nodelist, expire_time_var, fragment_name, models, vary_on):
        self.nodelist = nodelist
        if models == u'[]':
            self.models_name = []
        elif ',' in models:
            self.models_name = models.split(",")
        else:
            self.models_name = models
        self.expire_time_var = Variable(expire_time_var)
        self.fragment_name = fragment_name
        self.vary_on = vary_on

    def render(self, context):
        try:
            expire_time = self.expire_time_var.resolve(context)
        except VariableDoesNotExist:
            raise TemplateSyntaxError('"cache" tag got an unknkown variable: %r' % self.expire_time_var.var)
        try:
            expire_time = int(expire_time)
        except (ValueError, TypeError):
            raise TemplateSyntaxError('"cache" tag got a non-integer timeout value: %r' % expire_time)
        # Build a unicode key for this fragment and all vary-on's.
        cache_key = u':'.join([self.fragment_name] + [urlquote(resolve_variable(var, context)) for var in self.vary_on])
        if type(self.models_name) is list:
            models = [resolve_variable(x, context) for x in self.models_name if x]
        else:
            models = resolve_variable(self.models_name, context)

        def render_nodelist():
            return self.nodelist.render(context)
        
        return view_set_cache(cache_key, expire_time, models, cache_func=render_nodelist)

def do_cache(parser, token):
    """
    This will cache the contents of a template fragment for a given amount
    of time.

    Usage::

        {% load model_cache %}
        {% modelcache expire_time cashe_name (model_list|instance,[instance[,instance...]]|[]) [var1]  [var2] ... %}
            .. some expensive processing ..
        {% endmodelcache %}
    """
    nodelist = parser.parse(('endmodelcache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise TemplateSyntaxError(u"'%r' tag requires at least 2 arguments." % tokens[0])
    return CacheNode(nodelist, tokens[1], tokens[2], tokens[3], tokens[4:])

register.tag('modelcache', do_cache)
