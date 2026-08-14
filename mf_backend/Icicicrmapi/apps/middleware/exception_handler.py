"""
apps/middleware/exception_handler.py
======================================
Global exception handler middleware.

This middleware acts as the last-resort exception catcher for all unhandled
exceptions that escape the DRF exception handler (i.e., non-DRF exceptions
such as raw Python exceptions, database connection errors, etc.).

Responsibilities:
  - Catch any Exception not already handled by DRF's EXCEPTION_HANDLER.
  - Log the full traceback with correlation ID.
  - Return a standardized JSON error envelope (never expose a raw Django error page).
  - Preserve the correlation ID from CorrelationIdMiddleware.

Middleware execution order in settings.py MIDDLEWARE list:
  [0] SecurityMiddleware
  [1] CorrelationIdMiddleware     ← must be BEFORE this
  [2] RequestLoggingMiddleware    ← must be BEFORE this
  [3] ExceptionHandlerMiddleware  ← catches what DRF misses
  ...
  [N] CommonMiddleware

NOTE: DRF's own EXCEPTION_HANDLER in settings.py handles most API errors.
      This middleware handles OS-level, DB-connection, and setup errors.
"""

import json
import logging
import traceback

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from apps.common.constants.error_codes import ErrorCode

logger = logging.getLogger(__name__)

_INTERNAL_ERROR_BODY = {
    "success": False,
    "code": ErrorCode.GEN_INTERNAL_ERROR,
    "message": "An unexpected internal error occurred. Please try again or contact support.",
    "details": {},
}


class ExceptionHandlerMiddleware(MiddlewareMixin):
    """
    Catch-all middleware for unhandled exceptions.

    Converts any uncaught exception into a structured JSON 500 response,
    logs the full traceback, and attaches the correlation ID.
    """

    def process_exception(self, request, exception: Exception):
        """
        Called by Django when a view raises an unhandled exception.

        Args:
            request:   The current HttpRequest.
            exception: The uncaught exception instance.

        Returns:
            JsonResponse with HTTP 500, or None to let Django continue.
        """
        correlation_id = getattr(request, "correlation_id", "unknown")

        logger.error(
            "Unhandled exception | correlation_id=%s | path=%s | method=%s\n%s",
            correlation_id,
            request.path,
            request.method,
            traceback.format_exc(),
            exc_info=False,  # traceback already formatted above
        )

        response_body = {**_INTERNAL_ERROR_BODY}
        response_body["correlation_id"] = correlation_id

        response = JsonResponse(response_body, status=500)
        response["X-Correlation-ID"] = correlation_id
        return response
