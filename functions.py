# -*- coding: utf-8 -*-

from genshi.filters import HTMLSanitizer
from genshi.input import HTML
from django.core.urlresolvers import reverse as reverse_url

sanitizer = HTMLSanitizer(safe_attrs=HTMLSanitizer.SAFE_ATTRS|set(['style']))

def clean_html(s):
    try:
        c = str(HTML(s)|sanitizer)
    except:
        c = s.replace('<', '&lt;').replace('>', '&gt;')
    return c

def reverse(view_name, urlconf=None, *args, **kwargs):
    return reverse_url(view_name, urlconf=urlconf, args=args, kwargs=kwargs)