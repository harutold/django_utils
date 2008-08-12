# -*- coding: utf-8 -*-
from django import forms
from settings import MEDIA_URL
#from django.conf import CUSTOM_ADMIN_MEDIA
from django.contrib import admin

class SFieldSet:
    def __init__(self, field_sets):
        self.sets = field_sets + ((u'invalid', '--------'))
        self._i=-1
        
    def fieldset_number(self):
        return self._i
    
    def next_first(self):
        return self.sets[self._i+1][1]
    
    def set_next_and_return(self):
        self._i+= 1
        return self.sets[self._i][0]
    
    def __unicode__(self):
        return self.sets[self._i][0]

def humanize(inp_str):
    import re
    #return inp_str
    s = re.compile('<input[^>]*?type="text"[^>]*?value="(.*?)".*?/>').sub(r'<span>\1</span>', inp_str)
    s = re.compile('<input[^>]*?type="text".*?/>').sub('<span class="no">-----</span>', s)
    s = re.compile('<textarea[^>]*>(.+?)</textarea>').sub(r'<span>\1</span>', s)
    s = re.compile('<textarea[^>]*></textarea>').sub('<span class="no">-----</span>', s)
    s = re.compile('<label[^>]*><input[^>]*(type="radio"[^>]*checked|checked[^>]*type="radio")[^>]*>(.*?)</label>').sub(r'<span>\2</span>', s)
    s = re.compile('<label[^>]*><input[^>]*type="radio"[^>]*>.*?</label>').sub(u'', s)
    s = re.compile('<input[^>]*checked[^>]*>').sub(u'<span class="yes">Да</span>', s)
    s = re.compile('<input[^>]*>').sub(u'<span class="no">Нет<br/></span>', s)
    
    s = re.compile('<option[^>]*?selected[^>]*?>(.*?)</option>', re.DOTALL).sub('<span>\\1</span>', s)
    s = re.compile('<option[^>]*?>([^<]*?)</option>', re.DOTALL).sub('', s)
    s = re.compile('<\/?select[^>].*?>', re.DOTALL).sub('', s)
    s = re.compile('<\/?label[^>].*?>', re.DOTALL).sub('', s)
    return s

class WYSIWYGForm(forms.ModelForm): 
    class Media: 
        js = (
            "js/tiny_mce/tiny_mce_src.js",
            "admin/js/textareas.js",
            #''.join((MEDIA_URL,"js/mootols-beta12b_full_packed.js")),
            #''.join((MEDIA_URL, "js/validators.js")),
        )
        css = { 
            #'all': (''.join((MEDIA_URL,"css/tinypatch.css")),) 
        } 

class AdminWYSIWYG(admin.ModelAdmin):
    form = WYSIWYGForm