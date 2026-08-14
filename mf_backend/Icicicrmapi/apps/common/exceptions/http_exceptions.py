"""
apps/common/exceptions/http_exceptions.py
==========================================
HTTP-layer specific exceptions (raised in API views only).

These wrap DRF's native exceptions and should NOT be raised in services
or repositories. Only the API (view) layer should raise these.
"""

from rest_framework import status
from .base_exception import CRMBaseException


class BadRequestException(CRMBaseException):
    """HTTP 400 — Malformed request from the client."""
    message = "Bad request. Please check your input."
    code = "BAD_REQUEST"
    http_status = status.HTTP_400_BAD_REQUEST


class UnauthorizedException(CRMBaseException):
    """HTTP 401 — Authentication required."""
    message = "Authentication is required to access this resource."
    code = "UNAUTHORIZED"
    http_status = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(CRMBaseException):
    """HTTP 403 — Lacking permissions."""
    message = "You do not have permission to access this resource."
    code = "FORBIDDEN"
    http_status = status.HTTP_403_FORBIDDEN


class NotFoundException(CRMBaseException):
    """HTTP 404 — Endpoint or resource not found."""
    message = "The requested endpoint or resource was not found."
    code = "NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND


class MethodNotAllowedException(CRMBaseException):
    """HTTP 405 — HTTP method not supported on this endpoint."""
    message = "HTTP method not allowed."
    code = "METHOD_NOT_ALLOWED"
    http_status = status.HTTP_405_METHOD_NOT_ALLOWED


class TooManyRequestsException(CRMBaseException):
    """HTTP 429 — Rate limit exceeded."""
    message = "Too many requests. Please slow down."
    code = "RATE_LIMIT_EXCEEDED"
    http_status = status.HTTP_429_TOO_MANY_REQUESTS
