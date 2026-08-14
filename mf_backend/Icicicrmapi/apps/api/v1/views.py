"""
apps/api/v1/views.py
======================
API v1 — Base views and health check endpoints.
"""

import logging

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.authentication.backends import DelegatedJWTAuthentication as JWTAuthentication
from apps.common.responses.api_response import ApiResponse

logger = logging.getLogger(__name__)


# =============================================================================
# Health Check
# =============================================================================

class HealthCheckView(APIView):
    """
    GET /api/v1/health/
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        logger.debug("Health check probe received.")
        return Response(
            {
                "status": "success",
                "message": "ICICI CRM Backend Running"
            },
            status=status.HTTP_200_OK
        )


# =============================================================================
# Base API View
# =============================================================================

class BaseAPIView(APIView):
    """
    Base class for all authenticated v1 API views.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = []

    def get_correlation_id(self, request: Request) -> str:
        """Extract the correlation ID attached by CorrelationIdMiddleware."""
        return getattr(request, "correlation_id", "unknown")

    def success_response(
        self,
        data=None,
        message: str = "Request processed successfully.",
        code: str = "SUCCESS",
        status_code: int = status.HTTP_200_OK,
    ) -> Response:
        """
        Build and return a standard success response.
        """
        return ApiResponse(
            data=data, 
            message=message, 
            code=code, 
            http_status=status_code
        )
