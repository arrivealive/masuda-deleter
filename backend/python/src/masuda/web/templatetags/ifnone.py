# from django.template.defaulttags import register
from django import template

register = template.Library()

@register.filter
def ifnone(variable, alternative):
    if variable is None:
        return alternative
    return variable
