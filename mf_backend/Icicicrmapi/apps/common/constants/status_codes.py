"""
apps/common/constants/status_codes.py
=======================================
HTTP-aligned and business-domain status codes used across the project.

Rules:
  - Use these constants instead of raw integers in views and services.
  - HTTP status codes mirror Django REST Framework's status module but are
    re-exported here so all layers import from a single source.
  - Business status codes (non-HTTP) use the BIZ_ prefix.
"""

from rest_framework import status as drf_status

# =============================================================================
# HTTP 2xx — Success
# =============================================================================
HTTP_200_OK = drf_status.HTTP_200_OK
HTTP_201_CREATED = drf_status.HTTP_201_CREATED
HTTP_202_ACCEPTED = drf_status.HTTP_202_ACCEPTED
HTTP_204_NO_CONTENT = drf_status.HTTP_204_NO_CONTENT

# =============================================================================
# HTTP 3xx — Redirection
# =============================================================================
HTTP_301_MOVED_PERMANENTLY = drf_status.HTTP_301_MOVED_PERMANENTLY
HTTP_302_FOUND = drf_status.HTTP_302_FOUND

# =============================================================================
# HTTP 4xx — Client Errors
# =============================================================================
HTTP_400_BAD_REQUEST = drf_status.HTTP_400_BAD_REQUEST
HTTP_401_UNAUTHORIZED = drf_status.HTTP_401_UNAUTHORIZED
HTTP_403_FORBIDDEN = drf_status.HTTP_403_FORBIDDEN
HTTP_404_NOT_FOUND = drf_status.HTTP_404_NOT_FOUND
HTTP_405_METHOD_NOT_ALLOWED = drf_status.HTTP_405_METHOD_NOT_ALLOWED
HTTP_409_CONFLICT = drf_status.HTTP_409_CONFLICT
HTTP_422_UNPROCESSABLE_ENTITY = drf_status.HTTP_422_UNPROCESSABLE_ENTITY
HTTP_429_TOO_MANY_REQUESTS = drf_status.HTTP_429_TOO_MANY_REQUESTS

# =============================================================================
# HTTP 5xx — Server Errors
# =============================================================================
HTTP_500_INTERNAL_SERVER_ERROR = drf_status.HTTP_500_INTERNAL_SERVER_ERROR
HTTP_502_BAD_GATEWAY = drf_status.HTTP_502_BAD_GATEWAY
HTTP_503_SERVICE_UNAVAILABLE = drf_status.HTTP_503_SERVICE_UNAVAILABLE
HTTP_504_GATEWAY_TIMEOUT = drf_status.HTTP_504_GATEWAY_TIMEOUT

# =============================================================================
# Business Status Codes (non-HTTP, used inside response envelopes)
# =============================================================================

class BizStatus:
    """
    Non-HTTP business-layer status strings embedded in the API response envelope.

    Example:
        {
            "success": true,
            "biz_status": "LEAD_CREATED",
            "data": { ... }
        }
    """
    # Generic
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PARTIAL = "PARTIAL"

    # Authentication
    AUTH_SUCCESS = "AUTH_SUCCESS"
    AUTH_FAILED = "AUTH_FAILED"
    TOKEN_REFRESHED = "TOKEN_REFRESHED"
    TOKEN_REVOKED = "TOKEN_REVOKED"

    # ICICI CRM Integration
    ICICI_API_SUCCESS = "ICICI_API_SUCCESS"
    ICICI_API_FAILED = "ICICI_API_FAILED"
    ICICI_API_TIMEOUT = "ICICI_API_TIMEOUT"
    ICICI_API_RETRIED = "ICICI_API_RETRIED"

    # Data operations
    RECORD_CREATED = "RECORD_CREATED"
    RECORD_UPDATED = "RECORD_UPDATED"
    RECORD_DELETED = "RECORD_DELETED"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"

    # Validation
    VALIDATION_PASSED = "VALIDATION_PASSED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
