# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils.simplejson import dumps, loads
import csv

__all__ = ('render_to', 'json', 'allow_tags',  'csv_decor')

def simple_wrap(wrap, func):
    wrap.__module__ = func.__module__
    wrap.__name__ = func.__name__
    wrap.__doc__ = func.__doc__
    return wrap


def render_to(template_name):    
    def decor(func):
        
        def wrap(request, *args, **kwargs):
            res = func(request, *args, **kwargs)
            if type(res) is dict:
                context = RequestContext(request, res)
                return render_to_response(template_name, context)
            return res
        
        return simple_wrap(wrap, func)
    
    return decor

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
            
    return simple_wrap(wrap, func)

def allow_tags(func):
    func.allow_tags = True
    return func

def csv_decor(filename,  delimiter=";", encoding=None):
    def decor(func):
        def wrap(request, *args, **kwargs):
            resp = func(request, *args, **kwargs)
            if issubclass(resp.__class__, HttpResponse):
                return resp
            h = HttpResponse(mimetype="text/csv") 
            h['Content-Disposition'] = 'attacment; filename="%s"'%filename
            
            if encoding is not None:
                resp = [tuple([c.encode(encoding) for c in row]) for row in resp]

            dial = csv.excel()
            dial.delimiter = delimiter
            
            csv_writer = csv.writer(h, dialect=dial)
            csv_writer.writerows(resp)
            return h
        
        return simple_wrap(wrap, func)
    return decor
