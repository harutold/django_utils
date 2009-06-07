# -*- coding: utf-8 -*-
import csv

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.utils.simplejson import dumps, loads
from django.core.paginator import Paginator

__all__ = ('render_to', 'json', 'allow_tags',  'csv_decor', 'paged')

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

def paged(paged_list_name, per_page, per_page_var='per_page'):
    """
    Parse page from GET data and pass it to view. Split the
    query set returned from view.
    """
    
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            if not isinstance(result, dict):
                return result
            try:
                page = int(request.GET.get('page', 1))
            except (ValueError, KeyError):
                page = 1

            try:
                real_per_page = int(request.GET[per_page_var])
            except (ValueError, KeyError):
                real_per_page = per_page

            paginator = Paginator(result['paged_qs'], real_per_page)
            result[paged_list_name] = paginator.page(page).object_list
            result['page'] = page
            result['page_list'] = range(1, paginator.num_pages + 1)
            result['pages'] = paginator.num_pages
            result['per_page'] = real_per_page
            result['request'] = request
            return result
        return wrapper

    return decorator
