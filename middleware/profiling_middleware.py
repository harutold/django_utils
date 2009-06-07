
# -*- coding: utf-8 -*-

# Orignal version taken from http://www.djangosnippets.org/snippets/186/
# Original author: udfalkso
# Modified by: Shwagroo Team

import sys
import os
import re
import hotshot, hotshot.stats
import tempfile
import StringIO

from django.conf import settings
from django.db import connection

__all__ = ('ProfileMiddleware', )

words_re = re.compile( r'\s+' )

group_prefix_re = [
    re.compile( "^.*/django/[^/]+" ),
    re.compile( "^(.*)/[^/]+$" ), # extract module path
    re.compile( ".*" ),           # catch strange entries
]

class ProfileMiddleware(object):
    """
    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode, is available for superuser otherwise,
    but you really shouldn't add this middleware to any production configuration.

    WARNING: It uses hotshot profiler which is not thread safe.
    """
    def process_request(self, request):
        if (settings.DEBUG or request.user.is_superuser) and request.REQUEST.get('prof', None) is not None:
            self.tmpfile = tempfile.mktemp()
            self.prof = hotshot.Profile(self.tmpfile)
            self.q_before = self.mysql_stat()

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if (settings.DEBUG or request.user.is_superuser) and request.REQUEST.get('prof', None) is not None:
            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)

    def get_group(self, file):
        for g in group_prefix_re:
            name = g.findall( file )
            if name:
                return name[0]

    def get_summary(self, results_dict, sum):
        list = [ (item[1], item[0]) for item in results_dict.items() ]
        list.sort( reverse = True )
        list = list[:40]

        res = "      tottime\n"
        for item in list:
            res += "%4.1f%% %7.3f %s\n" % ( 100*item[0]/sum if sum else 0, item[0], item[1] )

        return res

    def summary_for_files(self, stats_str):
        stats_str = stats_str.split("\n")[5:]

        mystats = {}
        mygroups = {}

        sum = 0

        for s in stats_str:
            fields = words_re.split(s);
            if len(fields) == 7:
                time = float(fields[2])
                sum += time
                file = fields[6].split(":")[0]

                if not file in mystats:
                    mystats[file] = 0
                mystats[file] += time

                group = self.get_group(file)
                if not group in mygroups:
                    mygroups[ group ] = 0
                mygroups[ group ] += time

        return "<pre>" + \
               " ---- By file ----\n\n" + self.get_summary(mystats,sum) + "\n" + \
               " ---- By group ---\n\n" + self.get_summary(mygroups,sum) + \
               "</pre>"

    def process_response(self, request, response):
        if (settings.DEBUG or request.user.is_superuser) and request.REQUEST.get('prof', None) is not None:
            self.prof.close()

            out = StringIO.StringIO()
            old_stdout = sys.stdout
            sys.stdout = out

            stats = hotshot.stats.load(self.tmpfile)
            stats.sort_stats('time', 'calls')
            stats.print_stats()

            sys.stdout = old_stdout
            stats_str = out.getvalue()

            self.q_all = self.mysql_stat() - self.q_before - 1

            if response and response.content and stats_str:
                response.content = "<pre>" + stats_str + "</pre>"

            response.content = "\n".join(response.content.split("\n")[:40])

            response.content += self.summary_for_files(stats_str)
            if self.q_all > -1:
                response.content += u"<pre>-----MySQL stats-----\n\nКоличество запросов к базе: %s \n\n</pre>"%self.q_all

            os.unlink(self.tmpfile)

        return response

    def mysql_stat(self):
        if settings.DATABASE_ENGINE == 'mysql':
            cursor = connection.cursor()
            cursor.execute("show status where Variable_name='Questions'")
            return int(cursor.fetchone()[1])
        return 0
    
#show status where Variable_name="Questions";