import os
from django.conf import settings
from django.core import management

class InitDummyDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        path = os.path.join(settings.BASE_DIR, 'dummy/files/dummy.json')
        management.call_command('loaddata', path)

    def __call__(self, request):
        response = self.get_response(request)
        return response