from masudaapi.lib import user_getter

class CheckUserExistenceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_getter.get_or_create()
        response = self.get_response(request)
        return response