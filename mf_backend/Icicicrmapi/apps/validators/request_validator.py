"""
apps/validators/request_validator.py
=======================================
Request-level validators for DRF API views.

Responsibilities:
  - Validate full HTTP request objects (headers, query params, body).
  - Extract and validate pagination parameters.
  - Validate common request headers (Correlation-ID, Content-Type, etc.).
  - Provide a reusable mixin for APIView subclasses.

Design:
  - RequestValidator is NOT a DRF Serializer — it validates transport-level concerns.
  - Domain-level validation (business rules) belongs in BaseValidator subclasses.
  - Use RequestValidator in views BEFORE passing data to serializers or services.

Usage in a view:
    from apps.validators.request_validator import RequestValidator

    class SomeView(APIView):
        def post(self, request):
            RequestValidator.require_json_body(request)
            RequestValidator.validate_pagination(request)
            ...
"""

import logging
from typing import Any

from rest_framework.request import Request

from apps.common.exceptions.base_exception import ValidationException
from apps.common.constants.error_codes import ErrorCode

logger = logging.getLogger(__name__)


class RequestValidator:
    """
    Static utility class for request-level validation in API views.

    All methods raise ValidationException on failure.
    ValidationException is caught by the DRF custom exception handler
    and returned as a structured 422 response.
    """

    # -------------------------------------------------------------------------
    # Content-Type / Body
    # -------------------------------------------------------------------------

    @staticmethod
    def require_json_body(request: Request) -> None:
        """
        Assert that the request has a JSON body (Content-Type: application/json).

        Raises:
            ValidationException: If Content-Type is not application/json.
        """
        content_type = request.content_type or ""
        if "application/json" not in content_type:
            raise ValidationException(
                message="Request Content-Type must be 'application/json'.",
                code=ErrorCode.VAL_INVALID_CONTENT_TYPE,
                errors={
                    "Content-Type": [
                        f"Received '{content_type}', expected 'application/json'."
                    ]
                },
            )

    @staticmethod
    def require_non_empty_body(data: Any) -> None:
        """
        Assert that the parsed request body is a non-empty dict.

        Args:
            data: Parsed request.data from DRF.

        Raises:
            ValidationException: If body is empty or not a dict.
        """
        if not data or not isinstance(data, dict):
            raise ValidationException(
                message="Request body must be a non-empty JSON object.",
                code=ErrorCode.VAL_EMPTY_REQUEST_BODY,
                errors={"body": ["Request body is empty or not a valid JSON object."]},
            )

    # -------------------------------------------------------------------------
    # Pagination
    # -------------------------------------------------------------------------

    @staticmethod
    def validate_pagination(
        request: Request,
        max_page_size: int = 100,
    ) -> tuple[int, int]:
        """
        Extract and validate pagination query parameters.

        Query params:
            page      (int, default=1, min=1)
            page_size (int, default=20, min=1, max=max_page_size)

        Returns:
            tuple[page, page_size]

        Raises:
            ValidationException: If page or page_size are invalid.
        """
        errors = {}

        try:
            page = int(request.query_params.get("page", 1))
            if page < 1:
                raise ValueError
        except (TypeError, ValueError):
            errors["page"] = ["'page' must be a positive integer (>= 1)."]
            page = 1

        try:
            page_size = int(request.query_params.get("page_size", 20))
            if page_size < 1 or page_size > max_page_size:
                raise ValueError
        except (TypeError, ValueError):
            errors["page_size"] = [
                f"'page_size' must be between 1 and {max_page_size}."
            ]
            page_size = 20

        if errors:
            raise ValidationException(
                message="Invalid pagination parameters.",
                code=ErrorCode.VAL_INVALID_PAGINATION,
                errors=errors,
            )

        return page, page_size

    # -------------------------------------------------------------------------
    # Headers
    # -------------------------------------------------------------------------

    @staticmethod
    def require_correlation_id(request: Request) -> str:
        """
        Assert that X-Correlation-ID header is present.

        In most cases, CorrelationIdMiddleware auto-generates this — but for
        critical endpoints you may want to require it from the caller.

        Returns:
            The correlation ID string.

        Raises:
            ValidationException: If header is absent.
        """
        correlation_id = request.headers.get("X-Correlation-ID", "")
        if not correlation_id:
            raise ValidationException(
                message="Missing required header: X-Correlation-ID.",
                code=ErrorCode.VAL_MISSING_HEADER,
                errors={"X-Correlation-ID": ["This header is required."]},
            )
        return correlation_id

    # -------------------------------------------------------------------------
    # Query Parameters
    # -------------------------------------------------------------------------

    @staticmethod
    def require_query_params(request: Request, params: list[str]) -> None:
        """
        Assert that all listed query parameters are present and non-empty.

        Args:
            request: The DRF request.
            params:  List of required query param names.

        Raises:
            ValidationException: If any param is missing or empty.
        """
        missing = [p for p in params if not request.query_params.get(p)]
        if missing:
            raise ValidationException(
                message=f"Missing required query parameters: {', '.join(missing)}",
                code=ErrorCode.VAL_MISSING_REQUIRED_FIELD,
                errors={p: ["This query parameter is required."] for p in missing},
            )
