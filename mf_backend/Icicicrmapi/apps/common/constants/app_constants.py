"""
apps/common/constants/app_constants.py
=======================================
Application-wide constants and enumerations.

Rules:
  - No magic strings in business logic — import from here
  - Use Python Enum for strongly-typed constant groups
"""

from enum import Enum


# =============================================================================
# HTTP / API
# =============================================================================

class ApiVersion(str, Enum):
    V1 = "v1"


class ContentType(str, Enum):
    JSON = "application/json"
    FORM = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"


# =============================================================================
# Generic Entity States
# =============================================================================

class RecordStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"
    PENDING = "PENDING"
    SUSPENDED = "SUSPENDED"


# =============================================================================
# Sort / Pagination
# =============================================================================

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


# =============================================================================
# Date / Time
# =============================================================================

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
IST_TIMEZONE = "Asia/Kolkata"


# =============================================================================
# Header names
# =============================================================================

class Headers(str, Enum):
    CORRELATION_ID = "X-Correlation-ID"
    REQUEST_ID = "X-Request-ID"
    CLIENT_ID = "X-Client-ID"
    AUTHORIZATION = "Authorization"
    CONTENT_TYPE = "Content-Type"


# =============================================================================
# Token types
# =============================================================================

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    API_KEY = "api_key"


# =============================================================================
# External Integration
# =============================================================================

class ICICIEndpointGroup(str, Enum):
    """Logical groupings of ICICI CRM API endpoint categories."""
    CUSTOMER = "customer"
    LEAD = "lead"
    POLICY = "policy"
    CLAIM = "claim"
    AUTH = "auth"
