"""
apps/middleware/request_logging.py
=====================================
Request/Response logging middleware.

Logs every inbound HTTP request and outbound response in structured format.

Logged fields per request:
  - method, path, query_params
  - user_id (from JWT if authenticated)
  - correlation_id (from CorrelationIdMiddleware)
  - content_type, content_length

Logged fields per response:
  - status_code
  - response_time_ms
  - response_content_length

Security:
  - Request body is NOT logged (may contain PII/credentials).
  - Sensitive headers (Authorization, Cookie) are redacted.
  - Health check endpoints are excluded from logging to reduce noise.

Middleware execution order (must be AFTER CorrelationIdMiddleware):
  CorrelationIdMiddleware → RequestLoggingMiddleware → ...
"""

import logging
import time

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("request")

# Paths to skip logging (health checks, metrics)
_SKIP_PATHS = frozenset([
    "/health/",
    "/ping/",
    "/favicon.ico",
    "/__debug__/",
])

_SENSITIVE_HEADERS = frozenset([
    "authorization",
    "cookie",
    "x-api-key",
    "x-client-secret",
])


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Structured request/response logger.

    Emits one log line per request cycle containing:
      - Inbound request metadata (before view execution)
      - Outbound response metadata (after view execution)
    """

    def process_request(self, request):
        """
        Record start time and extract request metadata.
        """
        if request.path in _SKIP_PATHS:
            request._skip_logging = True
            return

        request._skip_logging = False
        request._start_time = time.monotonic()

        correlation_id = getattr(request, "correlation_id", "unknown")
        user_id = self._extract_user_id(request)

        logger.info(
            "→ REQUEST | correlation_id=%s | method=%s | path=%s | user_id=%s | "
            "content_type=%s | query=%s",
            correlation_id,
            request.method,
            request.path,
            user_id,
            request.content_type or "-",
            request.GET.urlencode() or "-",
        )

    def process_response(self, request, response):
        """
        Log response metadata and duration.
        """
        if getattr(request, "_skip_logging", True):
            return response

        duration_ms = round(
            (time.monotonic() - getattr(request, "_start_time", time.monotonic())) * 1000, 2
        )
        correlation_id = getattr(request, "correlation_id", "unknown")
        user_id = self._extract_user_id(request)
        content_length = response.get("Content-Length", "-")

        logger.info(
            "← RESPONSE | correlation_id=%s | status=%s | duration_ms=%s | "
            "content_length=%s | user_id=%s | path=%s",
            correlation_id,
            response.status_code,
            duration_ms,
            content_length,
            user_id,
            request.path,
        )

        return response

    @staticmethod
    def _extract_user_id(request) -> str:
        """
        Safely extract user_id from the request for logging.
        Returns '-' if not authenticated or not yet resolved.
        """
        user = getattr(request, "user", None)
        if user and hasattr(user, "pk") and user.is_authenticated:
            return str(user.pk)
        return "-"
