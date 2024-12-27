from .models import Tenant

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        domain = request.get_host()
        print(domain)
        request.tenant = Tenant.objects.filter(domain=domain).first()
        return self.get_response(request)

