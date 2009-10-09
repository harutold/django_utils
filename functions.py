# -*- coding: utf-8 -*-

import re
from genshi.filters import HTMLSanitizer
from genshi.input import HTML
from django.core.urlresolvers import reverse as reverse_url
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.models import User

__all__ = ('clean_html', 'reverse', 'redirect', 'fallback_to', 'capitalize', 'notify', 'flatatt', 'filesize_generic',
           'notify_admins', 'clean_tiny_mce_prefix')

sanitizer = HTMLSanitizer(safe_attrs=HTMLSanitizer.SAFE_ATTRS|set(['style']))

def clean_html(s):
    try:
        c = str(HTML(s)|sanitizer)
    except:
        c = s.replace('<', '&lt;').replace('>', '&gt;')
    return c

def reverse(view_name, urlconf=None, *args, **kwargs):
    if type(view_name) is str and not urlconf and '.' not in view_name:
        urlconf = 'urls'
    return reverse_url(view_name, urlconf=urlconf, args=args, kwargs=kwargs)

def redirect(*args, **kwargs):
    return HttpResponseRedirect(reverse(*args, **kwargs))

def fallback_to(template_name, res={}):
    from django_utils.middleware import get_request
    context = RequestContext(get_request(), res)
    return render_to_response(template_name, context)

def capitalize(s):
    if not s or type(s) not in (str, unicode):
        return s
    s = s.strip()
    return s[0].upper() + s[1:]

def notify(user, message):
    from django.contrib.auth.models import Message
    user.message_set.create(message=message)
    
def flatatt(attrs):
    #Вместо from django.forms.util import flatatt
    from django.utils.html import escape
    return u''.join([u' %s="%s"' % (k, escape(v)) for k, v in attrs.items()])

def filesize_generic(fieldname):
    def filesize(self):
        fsize = getattr(self, fieldname).size
        
        if fsize < 1024:
            return str(fsize) + ' bytes'
        elif fsize < 1048576:
            return str(fsize/1024) + ' kB'
        else:
            return str(fsize/1048576) + ' MB'
    filesize.short_description = u'размер файла'
    return filesize

def notify_admins(msg):
    map(lambda x: x.message_set.create(message=msg),
        User.objects.filter(is_staff=True))

def clean_tiny_mce_prefix(str):
    return re.compile('''(<img[^>]+src\=["'])(.[\.\/]+)/media''').sub(r'\1/media', str)
