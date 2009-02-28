# -*- coding: utf-8 -*-
import os

from django.conf import settings

__all__ = ('AjaxDebug',)

class AjaxDebug(object):
    # Отключает кеширование в опере.
    # Вынужденная мера для многоязычных сайтов,
    # в которых при переключении языка не меняется урл.
    
    def process_response(self, request, response):
        if settings.DEBUG and request.is_ajax():
            filename = os.path.join(settings.MEDIA_ROOT, 'last_ajax_request.html')
            f = open(filename, 'w')
            f.write(response.content)
            f.close()
        return response
