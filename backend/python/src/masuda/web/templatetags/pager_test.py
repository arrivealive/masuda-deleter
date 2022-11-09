# from django.template.defaulttags import register
from django import template
from django.core import paginator

register = template.Library()

@register.filter
def pager_test(page_obj:paginator.Page):
    page_obj.paginator.num_pages
    return len(page_obj.object_list), page_obj.end_index(), page_obj.paginator.num_pages