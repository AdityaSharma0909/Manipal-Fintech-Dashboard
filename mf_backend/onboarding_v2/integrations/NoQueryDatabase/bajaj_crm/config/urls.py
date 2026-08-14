from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from crm_integration.views import BranchByPincodeView


def health_check(request):
    """Simple liveness probe for load balancers and container orchestration."""
    return JsonResponse({"status": "ok"}, status=200)


urlpatterns = [
    path('admin/', admin.site.urls),

    # Liveness / health probe (unauthenticated, used by load balancers / k8s)
    path('health/', health_check, name='health-check'),

    # API endpoints
    path('api/branches/by-pincode/', BranchByPincodeView.as_view(), name='branches-by-pincode'),
    path('api/bajajfinservo/', include('crm_integration.urls')),

    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
