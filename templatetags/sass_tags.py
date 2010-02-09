# -*- coding: utf-8 -*-
import os
from warnings import warn

from django.template import Library, Node, TemplateSyntaxError
from django.conf import settings
from subprocess import Popen, PIPE

sass_dir = getattr(settings, 'SASS_DIR', 'media/css/')
sass_path = os.path.join(settings.CURDIR, sass_dir)
register = Library()

@register.simple_tag
def sass_to_file(args):
    content, chunks = [], []
    for arg in args.split():
        chunks.append(arg.rsplit('.')[0])
        path = os.path.join(sass_path, arg)
        
        if not os.path.isfile(path):
            raise TemplateSyntaxError(u'Sass file %s does not exist' % path)
        f = open(path)
        content.append(f.read().decode('utf-8'))
        f.close()
    output = '-'.join(chunks) + '.css'
    content = u'\n'.join(content)
    cssfile = os.path.join(sass_dir, output)
    csspath = os.path.join(sass_path, output)
    
    try:
        import sass # Пока тут
        css = sass.convert(content)
        f = open(csspath, 'w')
        f.write(css)
        f.close()
    except:
        warn('unable to parse file %s' % arg)
        p = Popen('sass --stdin %s' % csspath, shell=True, stdin=PIPE, stdout=PIPE)
        p.communicate(content.encode('utf-8'))
    return u'<link rel="stylesheet" href="/%s" type="text/css"></style>' % cssfile

