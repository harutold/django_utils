# -*- coding: utf-8 -*-

from django.core.management.base import NoArgsCommand
from os import walk, unlink
from os.path import join

class Command(NoArgsCommand):
    
    help ='Removes all *.pyc and *.pyo files in project'
    
    def handle_noargs(self, **kwargs):
        map(unlink, reduce(lambda x,y: x+y, (x for x in [[join(d,f) for f in fs if f.endswith('.pyc') or f.endswith('.pyo')] for d,_,fs in walk('.')] if x)))