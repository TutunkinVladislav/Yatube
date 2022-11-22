from django.core.paginator import Paginator

from .constants import SHOW_TEN_POSTS


def get_paginator(query, request):
    paginator = Paginator(query, SHOW_TEN_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
