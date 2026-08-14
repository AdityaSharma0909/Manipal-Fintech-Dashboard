# apps.middleware — Django middleware package.
#
# Middleware load order (configured in settings.py MIDDLEWARE list):
#   1. CorrelationIdMiddleware    — assigns X-Correlation-ID
#   2. RequestLoggingMiddleware   — logs request/response metadata
#   3. ExceptionHandlerMiddleware — catch-all JSON 500 for unhandled exceptions

from apps.middleware.correlation_id import CorrelationIdMiddleware
from apps.middleware.request_logging import RequestLoggingMiddleware
from apps.middleware.exception_handler import ExceptionHandlerMiddleware

__all__ = [
    "CorrelationIdMiddleware",
    "RequestLoggingMiddleware",
    "ExceptionHandlerMiddleware",
]
