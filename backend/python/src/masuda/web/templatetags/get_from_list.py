# from django.template.defaulttags import register
from django import template

register = template.Library()

@register.filter
def get_item(tuple, key):
    return tuple[key]
