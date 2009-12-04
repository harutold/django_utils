# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand
from os.path import dirname, join, isfile
import re
from StringIO import StringIO
from django.db.models import get_models, get_apps, get_model
from django.db import connection, transaction
from django.contrib.contenttypes.models import ContentType
from django.utils.termcolors import colorize
from django.template import Template, Context

def get_model(app, model):
    try:
        cls = ContentType.objects.get(app_label=app.lower(), model=model.lower()).model_class()
    except ContentType.DoesNotExist:
        raise Exception('content_type not found for %s.%s' % (app, model))
    return cls


def prepare(code):
    """
    \\pk:app.model
    \\content_type_id:app.model
    \\table:app.model
    """
    for r in re.compile('\\\(\w+:\w+\.\w+)').findall(code):
        action, app, model = re.compile('(\w+)').findall(r)
        cls = get_model(app, model)
        if not cls:
            raise Exception, "model not found %s.%s" % (app, model)
        r = '\\' + r
        if action == 'pk':
            code = code.replace(r, str(cls._meta.pk.get_attname()))
        elif action == 'table':
            code = code.replace(r, str(cls._meta.db_table))
        elif action == 'content_type_id':
            code = code.replace(r, str(ContentType.objects.get(app_label=app, model=model.lower()).pk))
    return code


class Command(NoArgsCommand):
    
    help = 'Creates triggers'
    
    def handle_noargs(self, **kwargs):

        actions = {
            'create': 'INSERT',
            'save': 'UPDATE',
            'delete': 'DELETE'
        }

        t_re = re.compile(r'([\w"]+)\.(\w+)\s+>>>(.+?)<<<', re.DOTALL + re.UNICODE)
        tmpl = Template(open(join(dirname(__file__), 'create.sql')).read())
        queries = []
        q = {}
        for _app in get_apps():
            path = dirname(_app.__file__)
            filename = join(path, 'triggers.sql')
            if isfile(filename):
                text = open(filename).read()
                for model, action, code in t_re.findall(text):
                    _model = None
                    table = None
                    if not model.startswith('"'):
                        try:
                            _model = get_model(_app.__name__.replace('.models', ''), model.lower())
                            table = _model._meta.db_table
                        except:
                            raise Exception('unknown model "%s"' % model)
                    else:
                        table = model.lstrip('"').rstrip('"')

                    try:
                        event = actions[action]
                    except KeyError:
                        raise Exception('unknown trigger type "%s"' % action)

                    if _model:
                        model_name = _model.__name__.lower()
                    else:
                        model_name = table
                    
                    code = ''.join(" "*16 + x for x in StringIO(code).readlines())
                    code = prepare(code)
                    
                    if _model not in q:
                        q[_model] = []
                    
                    q[_model].append((_model, action, table, tmpl.render(Context({
                            'model_name': model_name,
                            'action': action,
                            'table_name': table,
                            'code': code,
                            'event': actions[action]
                    }))))
                    
                    queries.append((_model, action, table, tmpl.render(Context({
                        'model_name': model_name,
                        'action': action,
                        'table_name': table,
                        'code': code,
                        'event': actions[action]
                    }))))

        cursor = connection.cursor()
        
        for m in reversed(sorted(q.keys())):
            if m:
                print colorize('%s.%s' % (m._meta.app_label, m.__name__), opts=('bold',))
            else:
                print 'raw tables'
            
            for model, action, table, sql in q[m]:
                def dt():
                    try:
                        cursor.execute("DROP TRIGGER %s_handle ON %s" % (action, table))
                        transaction.commit()
                    except:
                        transaction.rollback() 

                transaction.commit_manually(dt)()

                model_name = '"%s"' % table
                if model:
                    model_name = '%s.%s' % (model._meta.app_label, model.__name__)
            
                if m:
                    print colorize('\t%s' % action, opts=('bold',)),
                else:
                    print colorize('\t%s %s' % (table, action), opts=('bold',)),
        
                def ct():
                    try:
                        cursor.execute(sql)
                        print colorize('[OK]', fg='green', opts=('bold',))
                        transaction.commit()
                    except Exception, (e,):
                        print colorize('[ERROR]', fg='red', opts=('bold', ))
                        print '>'*50
                        print e,
                        print '<'*50
                        transaction.rollback()

                transaction.commit_manually(ct)()