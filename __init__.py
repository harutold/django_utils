# lib imports
from cache import *
from decorators import *
from functions import *
from email_auth_backend import *
from form_utils import *
import middleware ## !!!! <--captcha!!!
from filterspecs import EmptyStringFilterSpec

# native django imports
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import NoReverseMatch
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_unicode