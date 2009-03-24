#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist

register = Library()

@register.filter
def num(val):
    if type(val) in [int, float]:
        return val
    else:
        #спорно
        return int(val)

@register.filter
def mult(value, arg):
    "Multiplies the arg and the value"
    return num(value) * num(arg)

@register.filter
def sub(value, arg):
    "Subtracts the arg from the value"
    return num(value) - num(arg)

@register.filter
def div(value, arg):
    "Divides the value by the arg"
    return num(value) / num(arg)

@register.filter
def rev(value):
    "Returns 1/x"
    try:
        return 1.0 / num(value)
    except ZeroDivisionError:
        return None
