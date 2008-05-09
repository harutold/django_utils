# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

def render_to(template_name):
    
    def decor(func):
        
        def wrap(request, *args, **kwargs):
            res = func(request, *args, **kwargs)
            if type(res) is dict:
                context = RequestContext(request, res)
                return render_to_response(template_name, context)
            return res

        wrap.__name__ = func.__name__
        return wrap
    
    return decor


def json(func):
    
    def wrap(*args, **kwargs):
        resp = func(*args, **kwargs)
        if resp.has_key('request'):
            del resp['request']
        return HttpResponse(encode(resp))

    wrap.__name__ = func.__name__
    return wrap