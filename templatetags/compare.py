#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""FROM http://www.djangosnippets.org/snippets/177/ """

from django import template
from django.utils.encoding import force_unicode
import re

register = template.Library()


    
class IfInNode(template.Node):
    '''
    Like {% if %} but checks for the first value being in the second value (if a list). Does not work if the second value is not a list.
    '''
    def __init__(self, var1, var2, nodelist_true, nodelist_false, negate):
        self.var1, self.var2 = var1, var2
        self.nodelist_true, self.nodelist_false = nodelist_true, nodelist_false
        self.negate = negate

    def __str__(self):
        return "<IfNode>"

    def render(self, context):
        val1 = template.resolve_variable(self.var1, context)
        val2 = template.resolve_variable(self.var2, context)
        try:
            val2 = list(val2)
            if (self.negate and val1 not in val2) or (not self.negate and val1 in val2):
                return self.nodelist_true.render(context)
            return self.nodelist_false.render(context)
        except TypError:
            return ""

def ifin(parser, token, negate):
    bits = token.contents.split()
    if len(bits) != 3:
        raise template.TemplateSyntaxError, "%r takes two arguments" % bits[0]
    end_tag = 'end' + bits[0]
    nodelist_true = parser.parse(('else', end_tag))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse((end_tag,))
        parser.delete_first_token()
    else: nodelist_false = template.NodeList()
    return IfInNode(bits[1], bits[2], nodelist_true, nodelist_false, negate)

register.tag('ifin', lambda parser, token: ifin(parser, token, False))
