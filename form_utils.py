# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib import admin
from django.forms import DateField

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

DATE_INPUT_FORMATS = getattr(settings, "WYSIWYG_DATE_INPUT_FORMATS", None)

class WYSIWYGForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(WYSIWYGForm, self).__init__(*args, **kwargs)
        
        if DATE_INPUT_FORMATS:
            map(lambda x: x.__setattr__('input_formats', DATE_INPUT_FORMATS), \
                filter(lambda y: y.__class__ == DateField, self.fields.values()))
    
    class Media: 
        js = (
            "js/tiny_mce/tiny_mce_src.js",
            "admin/js/textareas.js",
        )

class AdminWYSIWYG(admin.ModelAdmin):
    form = WYSIWYGForm