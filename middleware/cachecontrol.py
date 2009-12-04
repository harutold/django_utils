# -*- coding: utf-8 -*-
from django.conf import settings

__all__ = ('NoCacheOpera',)

class NoCacheOpera(object):
    # Отключает кеширование в опере.
    # Вынужденная мера для многоязычных сайтов,
    # в которых при переключении языка не меняется урл.
    
    def process_response(self, request, response):
        if request.META.get('HTTP_USER_AGENT', '').find('Opera') >= 0:
            if not request.get_full_path().find(settings.MEDIA_URL) == 0:
                response['cache-control'] = 'no-cache'
        return response
