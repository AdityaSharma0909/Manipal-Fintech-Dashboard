"""
apps/middleware/correlation_id.py
===================================
Correlation ID middleware.

Assigns a unique X-Correlation-ID to every incoming request.
The ID is:
  - Read from the inbound X-Correlation-ID header (if provided by client/gateway)
  - Auto-generated (UUID4) if not present
  - Stored on the request object as request.correlation_id
  - Injected into every outbound response header
  - Available to all loggers via threading.local (set in log record factory)

Placement: FIRST in MIDDLEWARE list (after CorsMiddleware).

Usage (in views/services):
    # The middleware sets it — access via request.correlation_id
    correlation_id = request.correlation_id
"""

import logging
import threading
import uuid
from typing import Callable

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

# Thread-local store so correlation_id is accessible anywhere in the request thread
_thread_local = threading.local()

CORRELATION_ID_HEADER = "HTTP_X_CORRELATION_ID"
RESPONSE_HEADER = "X-Correlation-ID"


def get_current_correlation_id() -> str:
    """Return the correlation ID for the current request thread."""
    return getattr(_thread_local, "correlation_id", "")


class CorrelationIdMiddleware:
    """
    Django WSGI middleware that assigns a correlation ID to every request.

    Compatible with both function-based and class-based views.
    """

    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Read from inbound header or generate a fresh UUID
        correlation_id = request.META.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())

        # Attach to request and thread-local for downstream access
        request.correlation_id = correlation_id
        _thread_local.correlation_id = correlation_id

        # Inject into log records automatically
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.correlation_id = correlation_id
            return record

        logging.setLogRecordFactory(record_factory)

        logger.debug("Correlation ID assigned: %s", correlation_id)

        response: HttpResponse = self.get_response(request)

        # Echo correlation ID in the response header
        response[RESPONSE_HEADER] = correlation_id

        # Clean up thread-local after response
        _thread_local.correlation_id = ""

        return response
