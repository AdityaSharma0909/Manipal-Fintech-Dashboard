"""
apps/common/exceptions/base_exception.py
==========================================
Central exception hierarchy and DRF custom exception handler.

Rules:
  - All custom exceptions inherit from CRMBaseException
  - Business layer raises domain exceptions (NOT HTTP-aware)
  - API layer catches and converts to HTTP responses via DRF handler
  - custom_exception_handler is registered in settings.REST_FRAMEWORK
"""

import logging
from typing import Optional, Dict, Any

from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


# =============================================================================
# Base Domain Exception
# =============================================================================

class CRMBaseException(Exception):
    """
    Base class for all ICICI CRM domain exceptions.

    Attributes:
        message     : Human-readable error message.
        code        : Internal error code (maps to error_codes.py).
        details     : Optional structured dict with extra context.
        http_status : Suggested HTTP status code (used by exception handler).
    """

    message: str = "An unexpected error occurred."
    code: str = "INTERNAL_ERROR"
    http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        http_status: Optional[int] = None,
    ):
        self.message = message or self.__class__.message
        self.code = code or self.__class__.code
        self.details = details or {}
        self.http_status = http_status or self.__class__.http_status
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# =============================================================================
# Domain-Level Exceptions (business layer raises these)
# =============================================================================

class ResourceNotFoundException(CRMBaseException):
    """Raised when a requested resource does not exist."""
    message = "The requested resource was not found."
    code = "RESOURCE_NOT_FOUND"
    http_status = status.HTTP_404_NOT_FOUND


class DuplicateResourceException(CRMBaseException):
    """Raised when attempting to create a resource that already exists."""
    message = "A resource with the given identifier already exists."
    code = "DUPLICATE_RESOURCE"
    http_status = status.HTTP_409_CONFLICT


class ValidationException(CRMBaseException):
    """Raised when input data fails business-level validation."""
    message = "Validation failed."
    code = "VALIDATION_ERROR"
    http_status = status.HTTP_422_UNPROCESSABLE_ENTITY


class UnauthorizedException(CRMBaseException):
    """Raised when a user is not authenticated."""
    message = "Authentication is required."
    code = "UNAUTHORIZED"
    http_status = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(CRMBaseException):
    """Raised when a user lacks permission to perform an action."""
    message = "You do not have permission to perform this action."
    code = "FORBIDDEN"
    http_status = status.HTTP_403_FORBIDDEN


class BusinessRuleException(CRMBaseException):
    """Raised when a business rule or constraint is violated."""
    message = "A business rule violation occurred."
    code = "BUSINESS_RULE_VIOLATION"
    http_status = status.HTTP_400_BAD_REQUEST


class ServiceUnavailableException(CRMBaseException):
    """Raised when a dependent internal service is unavailable."""
    message = "A required service is currently unavailable."
    code = "SERVICE_UNAVAILABLE"
    http_status = status.HTTP_503_SERVICE_UNAVAILABLE


# Aliases for easier migration
NotFoundException = ResourceNotFoundException
AuthenticationException = UnauthorizedException
ConflictException = DuplicateResourceException
AuthorizationException = ForbiddenException


# =============================================================================
# DRF Custom Exception Handler
# =============================================================================

def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """
    Global DRF exception handler.
    """
    # Local import to prevent circular dependency with settings -> REST_FRAMEWORK
    from rest_framework.views import exception_handler as drf_exception_handler
    from apps.common.responses.error_response import ErrorResponse

    logger.debug("Exception handler invoked: %s", type(exc).__name__)

    # --- Handle our domain exceptions ---
    if isinstance(exc, CRMBaseException):
        logger.warning(
            "Domain exception [%s]: %s | details=%s",
            exc.code, exc.message, exc.details,
        )
        return ErrorResponse(
            message=exc.message,
            code=exc.code,
            details=exc.details,
            http_status=exc.http_status,
        )

    # --- Delegate to DRF for its own exceptions ---
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Normalize DRF error format to match our standard envelope
        original_data = response.data
        response.data = {
            "success": False,
            "code": "DRF_ERROR",
            "message": _extract_drf_message(original_data),
            "details": original_data,
        }
        return response

    # --- Completely unhandled exception → 500 ---
    logger.critical(
        "Unhandled exception: %s",
        str(exc),
        exc_info=True,
    )
    return ErrorResponse(
        message="An internal server error occurred. Please contact support.",
        code="INTERNAL_SERVER_ERROR",
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


crm_exception_handler = custom_exception_handler


def _extract_drf_message(data: Any) -> str:
    """Extract a readable message string from DRF's error data."""
    if isinstance(data, dict):
        return data.get("detail", str(data))
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)
