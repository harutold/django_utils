# -*- coding: utf-8 -*-

from pickle import dumps
from django.core.cache import cache
from base64 import encodestring

def cache_get_only(name=None):
    
    def decor(func):
        _name_ = name
        if _name_ is None:
            _name_ = func.__name__

        def wrap(request, *args, **kwargs):
            if request.method == 'GET':
                _name = 'cached_view_' + _name_ + encodestring(dumps(args) + dumps(kwargs))[:-1]
                cached = cache.get(_name)
                if cached is None:
                    cached = func(request, *args, **kwargs)
                    cache.set(_name, cached)
                return cached
            else:
                return func(request, *args, **kwargs)

        wrap.__name__ = func.__name__
        return wrap

    return decor


def cache_all(name=None):
    
    def decor(func):
        _name_ = name
        if _name_ is None:
            _name_ = func.__name__
        
        def wrap(request, *args, **kwargs):
            _name = 'cached_view_' + _name_ + encodestring(dumps(args) + dumps(kwargs))[:-1]
            cached = cache.get(_name)
            if cached is None:
                cached = func(request, *args, **kwargs)
                cache.set(_name, cached)
            return cached

        wrap.__name__ = func.__name__

        return wrap
    
    return decor

def clear_cached(name, session=False, *args, **kwargs):
    name = 'cached_view_%s%s' % ( name, encodestring(dumps(args) + dumps(kwargs))[:-1] )
    cache.delete(name)