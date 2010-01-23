# -*- coding: utf-8 -*-

from django import template
from django_utils.middleware.threadlocals import get_request

register = template.Library()

# TODO: this old code requires refactoring
@register.inclusion_tag('pagination.html',takes_context=True)
def pagination(context, adjacent_pages=5):
    """
    Return the list of A tags with links to pages.
    """
    page_obj = context['page_obj']
    paginator = context['paginator']
    page_list = range(
        max(1, page_obj.number - adjacent_pages),
        min(paginator.num_pages, page_obj.number + adjacent_pages) + 1)

    if not 1 in page_list:
        page_list.insert(0,1)
        if not 2 in page_list:
            page_list.insert(1,'.')

    if not paginator.num_pages in page_list:
        if not paginator.num_pages - 1 in page_list:
            page_list.append('.')
        page_list.append(paginator.num_pages)
        
    request = context.get('request', None) or get_request()
    get_params = '&'.join(['%s=%s' % (x[0],','.join(x[1])) for x in
        request.GET.iteritems() if (not x[0] == 'page' and not x[0] == 'per_page')])
    get_params = '?%s&' % get_params if get_params else '?'

    return {
        'get_params': get_params,
        'page_obj': context['page_obj'],
        #'page': context['page'],
        #'pages': context['pages'],
        'page_list': page_list,
        #'per_page': context['per_page'],
        }
