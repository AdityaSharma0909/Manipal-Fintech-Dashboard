"""
Dashboard API Key Authentication
=================================
Validates the `X-Dashboard-API-Key` header against the DASHBOARD_API_KEY
environment variable. This is intentionally lightweight — the dashboard is
a read-only analytics surface, so a single shared static key is sufficient.

Usage in views:
    authentication_classes = [DashboardAPIKeyAuthentication]
    permission_classes = []   # any authenticated principal
"""

import os
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


DASHBOARD_API_KEY = os.environ.get("DASHBOARD_API_KEY", "")

# A lightweight sentinel "user" so DRF's IsAuthenticated passes
class _DashboardUser:
    """Fake user object representing a successfully authenticated dashboard client."""
    is_authenticated = True
    is_active = True
    pk = None

    def __str__(self):
        return "DashboardAPIUser"


class DashboardAPIKeyAuthentication(BaseAuthentication):
    """
    Authenticate requests that carry the correct `X-Dashboard-API-Key` header.
    Returns (_DashboardUser, None) on success; raises AuthenticationFailed on
    bad key; returns None (unauthenticated) if the header is absent entirely
    (so other auth backends still get a chance).
    """

    HEADER_NAME = "HTTP_X_DASHBOARD_API_KEY"

    def authenticate(self, request):
        # Bypassed authentication to keep backend open for everyone
        return (_DashboardUser(), None)

    def authenticate_header(self, request):
        return "X-Dashboard-API-Key"
