# -*- coding: utf-8 -*-

from pickle import dumps
from django.core.cache import cache
from base64 import encodestring
from django.dispatch import dispatcher
from django.db.models import signals
from django.utils.functional import curry
from django.utils.encoding import force_unicode

__all__ = ('set_cache_name', 'cache_all', 'cache_get_only', 'clear_cached', 'get_template_cache_name', 'connect_to_models')

CACHE_VIEW_PREFIX = 'cv_'
AUTH_VIEW_PREFIX = 'a_'
CACHE_NAME = 'cache_name'


def _clear_cached(name, *args, **kwargs):
    print 'cache cleared for %s' % name
    cache.delete(name)

def _cache(name, value):
    cache.set(name, value)
    print 'cache set for %s' % name
    return value

def get_cache_name(name, *args, **kwargs):
    if type(name) is not str:
        if hasattr(name, CACHE_NAME):
            name = getattr(name, CACHE_NAME)
        else:
            name = name.__module__.replace('.', '_') + '_' + name.__name__
    return CACHE_VIEW_PREFIX + name + encodestring(dumps((args, kwargs)))[:-1]

def set_cache_name(name):
    
    def decor(func):
        setattr(func, CACHE_NAME, name)
        return func
    
    return decor

def cache_get_only(models=[], auth=False):
    
    def decor(func):
        map(curry(connect_to_models, get_cache_name(func)), models)
        if auth:
            map(curry(connect_to_models, AUTH_VIEW_PREFIX + get_cache_name(func)), models)

        def wrap(request, *args, **kwargs):
            if request.method == 'GET':
                _name = get_cache_name(func, *args, **kwargs)
                if auth and request.user.is_authenticated():
                    _name = AUTH_VIEW_PREFIX + _name
                cached = cache.get(_name)
                if cached is None:
                    cached = _cache(_name, func(request, *args, **kwargs))
                return cached
            else:
                return func(request, *args, **kwargs)

        wrap.__module__ = func.__module__
        wrap.__name__ = func.__name__
        return wrap

    return decor

def cache_all(models=[], auth=False):
    
    def decor(func):
        map(curry(connect_to_models, get_cache_name(func)), models)
        if auth:
            map(curry(connect_to_models, AUTH_VIEW_PREFIX + get_cache_name(func)), models)

        def wrap(request, *args, **kwargs):
            _name = get_cache_name(func, *args, **kwargs)
            if auth and request.user.is_authenticated():
                _name = AUTH_VIEW_PREFIX + _name
            cached = cache.get(_name)
            if cached is None:
                cached = _cache(_name, func(request, *args, **kwargs))
            return cached
        
        wrap.__module__ = func.__module__
        wrap.__name__ = func.__name__
        return wrap
    
    return decor


def connect_to_models(name, model):
    signals.post_save.connect(curry(_clear_cached, name), sender=model, weak=False)
    signals.post_delete.connect(curry(_clear_cached, name), sender=model, weak=False)


def clear_cached(name, *args, **kwargs):
    _name = get_cache_name(name, *args, **kwargs)
    _clear_cached(_name)
    _clear_cached(AUTH_VIEW_PREFIX + _name)

def get_template_cache_name(name, *args):
    return u':'.join([name] + [force_unicode(var) for var in args])