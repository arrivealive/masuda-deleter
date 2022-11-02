# from django.template.defaulttags import register
from django import template
from django.core import paginator

register = template.Library()

@register.filter
def pager_dots(num, page_obj:paginator.Page):
    current = page_obj.number
    pager_arm_left_length = 10
    pager_arm_right_length = 10
    last = page_obj.paginator.num_pages
    if num == 1 and current - pager_arm_left_length > 2:
        return True
    if num == last - 1 and current + pager_arm_right_length < last - 1:
        return True
    return False
