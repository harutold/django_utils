# -*- coding: utf-8 -*-
import os
from warnings import warn

from django.template import Library, Node, TemplateSyntaxError
from django.conf import settings

sass_dir = getattr(settings, 'SASS_DIR', 'media/css/')
sass_path = os.path.join(settings.CURDIR, sass_dir)
register = Library()

@register.simple_tag
def sass_to_string(arg):
    path = os.path.join(sass_path, arg)
    if not os.path.isfile(path):
        raise TemplateSyntaxError(u'Sass file %s does not exist' % path)
    f = open(path)
    content = f.read()
    f.close()
    
    try:
        import sass # Пока тут
        css = sass.convert(content)
        css = u'<style>/*SASS file %s*/ \n %s</style>' % (arg, css)
    except:
        warn('unable to parse file %s' % arg)
        css = os.system('sass %s %s.css' % (path, path))
        cssdir = os.path.join(sass_dir, arg)
        css = u'<link rel="stylesheet" href="/%s.css" type="text/css"></style>' % cssdir
    return css
    