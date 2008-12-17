#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist

register = Library()

def num(val):
    if type(val) in [int, float]:
        return val
    else:
        #спорно
        return int(val)

def mult(value, arg):
    "Multiplies the arg and the value"
    return num(value) * num(arg)

def sub(value, arg):
    "Subtracts the arg from the value"
    return num(value) - num(arg)

def div(value, arg):
    "Divides the value by the arg"
    return num(value) / num(arg)

def rev(value):
    ""
    try:
        return 1 / num(value)
    except ZeroDivisionError:
        return None

register.filter('mult', mult)
register.filter('sub', sub)
register.filter('div', div)
register.filter('rev', rev)
