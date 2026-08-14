"""
config/urls.py
==============
Root URL configuration.
- Mounts admin, API v1, JWT auth endpoints under versioned prefixes.
- API versioning is path-based: /api/v1/...
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings

API_PREFIX = getattr(settings, "API_PREFIX", "api")

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # API v1 — all versioned routes live here
    path(f"{API_PREFIX}/v1/", include("apps.api.v1.urls", namespace="api_v1")),

    # OpenAPI Schema / Swagger / ReDoc
    path(f"{API_PREFIX}/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(f"{API_PREFIX}/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(f"{API_PREFIX}/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Debug toolbar (development only)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
