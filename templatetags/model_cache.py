#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from django.template import resolve_variable
from django.core.cache import cache
from django_utils import connect_to_models
from django.utils.encoding import force_unicode
from django.utils.http import urlquote
from django.utils.functional import curry

register = Library()

class RegisteredCaches(object):
    def __init__(self):
        self.caches = []
    
    def add_cache(self, models, name):
        if not (name in self.caches):
            print "cache setted: %s" % name
            map(curry(connect_to_models, name), models)
            self.caches.append(name)    

caches = RegisteredCaches()

class CacheNode(Node):
    def __init__(self, nodelist, expire_time_var, fragment_name, models, vary_on):
        self.nodelist = nodelist
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
        value = cache.get(cache_key)
        if value is None:
    #        print "\n\n\nNOT FROM CACHE"
            if self.models_name is not None:
                models = resolve_variable(self.models_name, context)
                if models:
                    caches.add_cache(models, cache_key)
            value = self.nodelist.render(context)
            if expire_time:
                cache.set(cache_key, value, expire_time)
            else:
                cache.set(cache_key, value)
    #    else:
    #        print "\n\n\n   FROM CACHE"
        return value

def do_cache(parser, token):
    """
    This will cache the contents of a template fragment for a given amount
    of time.

    Usage::

        {% load cache %}
        {% modelcache [expire_time] [fragment_name] [models] %}
            .. some expensive processing ..
        {% endcache %}

    This tag also supports varying by a list of arguments::

        {% load cache %}
        {% modelcache [expire_time] [fragment_name] [models] [var1] [var2] .. %}
            .. some expensive processing ..
        {% endcache %}

    Each unique set of arguments will result in a unique cache entry.
    """
    nodelist = parser.parse(('endmodelcache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise TemplateSyntaxError(u"'%r' tag requires at least 2 arguments." % tokens[0])
    if len(tokens) == 3 or tokens[3] == u'[]':
        models = None
    else:
        models = tokens[3]
    return CacheNode(nodelist, tokens[1], tokens[2], models, tokens[4:])

register.tag('modelcache', do_cache)
