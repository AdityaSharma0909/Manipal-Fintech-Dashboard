"""
apps/common/responses/error_response.py
=========================================
Standardized error response envelope.

Error envelope:
{
    "success": false,
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found.",
    "details": { ... }   ← optional field-level validation errors, trace info
}

Used by:
  - custom_exception_handler in base_exception.py
  - GlobalExceptionHandlerMiddleware
"""

from typing import Any, Optional, Dict
from rest_framework.response import Response
from rest_framework import status


class ErrorResponse(Response):
    """
    Standardized error response wrapper.

    Args:
        message    : Human-readable error message.
        code       : Internal error code string.
        details    : Optional structured details (field errors, trace, etc.)
        http_status: HTTP status code. Default: 400.
    """

    def __init__(
        self,
        message: str = "An error occurred.",
        code: str = "ERROR",
        details: Optional[Dict[str, Any]] = None,
        http_status: int = status.HTTP_400_BAD_REQUEST,
        **kwargs,
    ):
        envelope = {
            "success": False,
            "code": code,
            "message": message,
            "details": details or {},
        }
        super().__init__(data=envelope, status=http_status, **kwargs)
