# from django.template.defaulttags import register
from django import template
from masudaapi.models import Progress

register = template.Library()

@register.filter
def progress_can_stop(progress:Progress):
    if not progress.status in [Progress.STATUS.PENDING, Progress.STATUS.PROCESSING]:
        return False
    return True
