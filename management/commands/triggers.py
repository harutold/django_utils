# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand
from os.path import dirname, join, isfile
import re
from StringIO import StringIO
from django.db.models import get_models, get_apps
from django.db import connection
from django.contrib.contenttypes.models import ContentType


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

        models = dict((x.__name__, x._meta.db_table) for x in get_models())
        apps = (dirname(x.__file__) for x in get_apps())
        actions = {
            'create': 'INSERT',
            'save': 'UPDATE',
            'delete': 'DELETE'
        }

        t_re = re.compile(r'([\w"]+)\.(\w+)\s+>>>(.+?)<<<', re.DOTALL + re.UNICODE)

        queries = []
        for path in apps:
            filename = join(path, 'triggers.sql')
            if isfile(filename):
                text = open(filename).read()
                for model, action, code in t_re.findall(text):
                    if not model.startswith('"'):
                        try:
                            table = models[model]
                        except:
                            raise Exception('unknown model "%s"' % model)
                    else:
                        table = model.lstrip('"').rstrip('"')

                    try:
                        event = actions[action]
                    except KeyError:
                        raise Exception('unknown trigger type "%s"' % action)
                    code = ''.join(" "*16 + x for x in StringIO(code).readlines())

                    code = prepare(code)

                    queries.append((model, action, table, """
                    CREATE OR REPLACE FUNCTION %s_%s_handle() RETURNS trigger AS
                    $BODY$
                    %s
                    $BODY$
                    LANGUAGE 'plpgsql' VOLATILE
                    COST 100;

                    CREATE TRIGGER %s_handle
                      AFTER %s
                      ON %s
                      FOR EACH ROW
                      EXECUTE PROCEDURE %s_%s_handle();
                    """ % (action, table, code, action, event, table, action, table)))

        cursor = connection.cursor()

        for model, action, table, sql in queries:

            try:
                cursor.execute("DROP TRIGGER %s_handle ON %s" % (action, table))
            except:
                cursor.db.connection.rollback()

            print '-- creating %s %s trigger %s' % (model, action, '-'*20)

            try:
                cursor.execute(sql)
                print 'ok'
                cursor.db.connection.commit()
            except Exception, (e,):
                print 'ERROR'
                print e
                cursor.db.connection.rollback()
                break