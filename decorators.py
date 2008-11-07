# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils.simplejson import dumps, loads
import csv

__all__ = ('render_to', 'json', 'allow_tags',  'csv_decor')

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

def _is_subclass(t1, t2):
    for b in getattr(t1, '__bases__', ()):
        if b is t2 or _is_subclass(b, t2):
            return 1
    return 0

def json(func):
    
    def wrap(request, *args, **kwargs):
        if request.method == 'POST' and 'json' in request.POST:
            request.JSON = loads(request.POST['json'])
        else:
            request.JSON = {}
        resp = func(request, *args, **kwargs)
        if issubclass(resp.__class__, HttpResponse):
            return resp
        if type(resp) is dict and 'request' in resp:
            del resp['request']
        return HttpResponse(dumps(resp), mimetype='application/json')
            

    wrap.__module__ = func.__module__
    wrap.__name__ = func.__name__
    return wrap

def allow_tags(func):
    func.allow_tags = True
    return func

def csv_decor(filename,  delimiter=";"):
    def decor(func):
    
        def wrap(request, *args, **kwargs):
            resp = func(request, *args, **kwargs)
            if issubclass(resp.__class__, HttpResponse):
                return resp
            h = HttpResponse(mimetype="text/csv") 
            h['Content-Disposition'] = 'attacment; filename="%s"'%filename   

            dial = csv.excel()
            dial.delimiter = delimiter
            
            csv_writer = csv.writer(h, dialect=dial)
            csv_writer.writerows(resp)
            return h

        wrap.__module__ = func.__module__
        wrap.__name__ = func.__name__
        return wrap
    return decor
