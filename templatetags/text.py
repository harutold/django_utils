#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import template
from django.utils.encoding import force_unicode

register = template.Library()


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


def truncatesmart(value, limit=20):
    """
    Основано на http://www.djangosnippets.org/snippets/1259/
    
    Обрезает строку на заданном колличестве симовлов, выбирает все необрезаные слова и добавляет троеточие.
    Результат будет в разных ситуациях иметь разную длинну но не более limit+3. 
    
    Пример использования:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """
    
    try:
        limit = int(limit)
    except ValueError:
        return value
    newvalue = force_unicode(value)
    if len(newvalue) <= limit:
        return newvalue
    newvalue = newvalue[:limit]
    words = newvalue.split()
    if u' '.join(value.split()[:len(words)-1]) != newvalue:
        #Если последнее слово частично обрезано
        words = words[:-1]
    return u' '.join(words) + u'...'
    
register.filter('truncatesmart', truncatesmart)
register.filter('truncatechars', truncatechars)