

# customer_management_app/middleware.py

from django.shortcuts import redirect # type: ignore

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and not request.user.is_staff:
            return redirect('login')  # Redirect to login if not admin
        response = self.get_response(request)
        return response
