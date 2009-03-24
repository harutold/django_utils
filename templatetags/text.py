#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import template
from django.utils.encoding import force_unicode
import re

register = template.Library()

@register.filter
def truncatechars(value, limit=20):
    """
     Обрезает строку до limit символов и добавляет троеточие в конце
     итоговая строка равна limit+3 символов
    """
    try:
        limit = int(limit)
    except ValueError:
        return value
    value = unicode(value)
    if len(value) <= limit:
        return value
    value = value[:limit]
    return value + u'...'

@register.filter
def truncatesmart(value, limit=20):
    """
    Основано на http://www.djangosnippets.org/snippets/1259/
    
    Обрезает строку на заданном количестве симовлов, выбирает все необрезаные слова и добавляет троеточие.
    Результат будет в разных ситуациях иметь разную длинну но не более limit+3.
    
    Если первое слово длиннее, чем limit, возвращает truncatechars
    
    Пример использования:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """
    
    try:
        limit = int(limit)
    except ValueError:
        return value
    newvalue = force_unicode(value).replace('\n', ' ')
    truncated = ' ' not in (newvalue[limit-1:limit])
    
    if len(newvalue) <= limit:
        return newvalue
    newvalue = newvalue[:limit]
    
    words = newvalue.split()
    if truncated:
        #Если последнее слово частично обрезано
        words = words[:-1]
    if not words:
        return truncatechars(value, limit=limit)
    else:
        return u' '.join(words) + u'...'