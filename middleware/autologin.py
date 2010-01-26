# -*- coding: utf-8 -*-
from django.contrib.auth.models import User    
from django.contrib.auth import login
from django.http import HttpResponseRedirect

__all__ = ('AutoLogin',)

u'''
    Кривая реализация автозалогинивания по ссылке.
'''

class AutoLogin(object):
    """
        Looks for auth information in GET parameters and redirects after authenticating
    """
    def process_request(self, request):
        if 'autologin' in request.GET and 'autologincode' in request.GET:
            get = request.GET.copy()
            try:
                user = User.objects.get(pk=get.pop('autologin')[0])
            except User.DoesNotExist:
                pass
            else:
                if user.get_auth_code() == get.pop('autologincode')[0]:
                    # TODO: Сделать нормально, это никуда не годится!
                    user.backend = 'goouser.auth_backend.EmailBackend'
                    login(request, user)
            return HttpResponseRedirect(request.path + '?' + get.urlencode())
