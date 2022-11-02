# from django.template.defaulttags import register
from django import template

register = template.Library()

@register.filter
def percent(dividend, divisor):
    if divisor == 0:
        return 0
    return round(dividend / divisor * 100)
