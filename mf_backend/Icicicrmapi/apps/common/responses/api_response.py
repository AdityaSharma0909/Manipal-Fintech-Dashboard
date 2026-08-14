"""
apps/common/responses/api_response.py
======================================
Standardized API response envelope.

ALL API endpoints must return responses using ApiResponse or ErrorResponse.
This ensures a consistent JSON contract across the entire API surface.

Success envelope:
{
    "success": true,
    "code": "OK",
    "message": "Operation completed successfully.",
    "data": { ... },
    "meta": { "page": 1, "total": 100 }   ← optional pagination/meta
}

Usage in views:
    from apps.common.responses.api_response import ApiResponse
    return ApiResponse(data=serializer.data, message="Customer fetched.")
"""

from typing import Any, Optional, Dict
from rest_framework.response import Response
from rest_framework import status


class ApiResponse(Response):
    """
    Successful API response wrapper.

    Args:
        data      : The payload to return (dict, list, serializer.data, etc.)
        message   : Human-readable success message.
        code      : Internal success code. Default: "OK".
        http_status: HTTP status code. Default: 200.
        meta      : Optional metadata dict (pagination, counts, etc.)
    """

    def __init__(
        self,
        data: Any = None,
        message: str = "Operation completed successfully.",
        code: str = "OK",
        http_status: int = status.HTTP_200_OK,
        meta: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        envelope = {
            "success": True,
            "code": code,
            "message": message,
            "data": data,
        }
        if meta is not None:
            envelope["meta"] = meta

        super().__init__(data=envelope, status=http_status, **kwargs)


class CreatedResponse(ApiResponse):
    """Convenience 201 Created response."""

    def __init__(self, data: Any = None, message: str = "Resource created successfully.", **kwargs):
        super().__init__(data=data, message=message, code="CREATED", http_status=status.HTTP_201_CREATED, **kwargs)


class NoContentResponse(Response):
    """Convenience 204 No Content response."""

    def __init__(self, **kwargs):
        super().__init__(data=None, status=status.HTTP_204_NO_CONTENT, **kwargs)


class PaginatedResponse(ApiResponse):
    """
    Paginated list response.

    Wraps a DRF paginator result with standardized meta block.

    Usage in views:
        page = self.paginate_queryset(queryset)
        serializer = MySerializer(page, many=True)
        return PaginatedResponse(
            data=serializer.data,
            paginator=self.paginator,
        )
    """

    def __init__(
        self,
        data: Any,
        paginator: Any,
        message: str = "List fetched successfully.",
        **kwargs,
    ):
        meta = {
            "count": paginator.page.paginator.count if hasattr(paginator, "page") else None,
            "next": paginator.get_next_link() if hasattr(paginator, "get_next_link") else None,
            "previous": paginator.get_previous_link() if hasattr(paginator, "get_previous_link") else None,
        }
        super().__init__(data=data, message=message, meta=meta, **kwargs)
