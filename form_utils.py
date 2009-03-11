# -*- coding: utf-8 -*-
__all__ = ('SFieldSet', 'humanize', 'WYSIWYGForm', 'AdminWYSIWYG')

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
DELETE_FILES = getattr(settings, "WYSIWYG_DELETE_FILES", False)
TEXTAREAJS_PATH = getattr(settings, "WYSIWYG_TEXTAREAJS_PATH", "admin/js/textareas.js")
TINYMCE_PATH = getattr(settings, "WYSIWYG_TINYMCE_PATH", "js/tiny_mce/tiny_mce.js")

class WYSIWYGForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        from django_fields import RemovableFileFormField
        super(WYSIWYGForm, self).__init__(*args, **kwargs)
        
        if DATE_INPUT_FORMATS:
            map(lambda x: x.__setattr__('input_formats', DATE_INPUT_FORMATS), \
                filter(lambda y: y.__class__ == DateField, self.fields.values()))
        if DELETE_FILES:
            for key, f in self.fields.items():
                if issubclass(f.__class__, forms.FileField) and not f.required:
                    self.fields[key] = RemovableFileFormField(required = False, inst=self.instance, key=key)
                    self.fields[key].label = f.label
                    self.fields[key].help_text = f.help_text

    
    class Media: 
        js = (
            TINYMCE_PATH,
            TEXTAREAJS_PATH,
        )
        css = { 
            'all': (
                "css/tinypatch.css", # At least: tr.mceMenuItem td, tr.mceMenuItem th {line-height:normal;}
                ), 
        }

class AdminWYSIWYG(admin.ModelAdmin):
    form = WYSIWYGForm