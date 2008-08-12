# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils.simplejson import dumps, loads

__all__ = ('render_to', 'json', 'allow_tags')

def render_to(template_name):
    
    def decor(func):
        
        def wrap(request, *args, **kwargs):
            res = func(request, *args, **kwargs)
            if type(res) is dict:
                context = RequestContext(request, res)
                return render_to_response(template_name, context)
            return res

        wrap.__module__ = func.__module__
        wrap.__name__ = func.__name__
        return wrap
    
    return decor


def json(func):
    
    def wrap(request, *args, **kwargs):
        if request.method == 'POST' and 'json' in request.POST:
            request.JSON = loads(request.POST['json'])
        else:
            request.JSON = {}
        resp = func(request, *args, **kwargs)
        if type(resp) is dict and 'request' in resp:
            del resp['request']
        return HttpResponse(dumps(resp), mimetype='application/json')

    wrap.__module__ = func.__module__
    wrap.__name__ = func.__name__
    return wrap

def allow_tags(func):
    func.allow_tags = True
    return func
