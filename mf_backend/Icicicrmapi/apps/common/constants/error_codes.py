"""
apps/common/constants/error_codes.py
======================================
Centralised error code registry.

All error codes used in exception raising and API responses
are defined here as string constants.

Naming convention:
  <LAYER>_<DOMAIN>_<DESCRIPTION>
  e.g. DB_CUSTOMER_NOT_FOUND, ICICI_AUTH_FAILED, VAL_MISSING_FIELD

Group prefixes:
  GEN_   → Generic / infrastructure
  AUTH_  → Authentication / authorization
  VAL_   → Validation
  DB_    → Database / data layer
  ICICI_ → ICICI CRM integration
  BIZ_   → Business rule violations
"""


class ErrorCode:
    """
    Error code registry class.
    """

    # =============================================================================
    # Generic
    # =============================================================================
    GEN_INTERNAL_ERROR        = "GEN_INTERNAL_ERROR"
    GEN_SERVICE_UNAVAILABLE   = "GEN_SERVICE_UNAVAILABLE"
    GEN_NOT_FOUND             = "GEN_NOT_FOUND"
    GEN_DUPLICATE             = "GEN_DUPLICATE"
    GEN_TIMEOUT               = "GEN_TIMEOUT"
    GEN_BAD_REQUEST           = "GEN_BAD_REQUEST"
    GEN_RATE_LIMIT            = "GEN_RATE_LIMIT"

    # =============================================================================
    # Authentication / Authorization
    # =============================================================================
    AUTH_INVALID_CREDENTIALS  = "AUTH_INVALID_CREDENTIALS"
    AUTH_TOKEN_EXPIRED        = "AUTH_TOKEN_EXPIRED"
    AUTH_TOKEN_INVALID        = "AUTH_TOKEN_INVALID"
    AUTH_INSUFFICIENT_PERMS   = "AUTH_INSUFFICIENT_PERMS"
    AUTH_USER_INACTIVE        = "AUTH_USER_INACTIVE"
    AUTH_USER_NOT_FOUND       = "AUTH_USER_NOT_FOUND"

    # =============================================================================
    # Validation
    # =============================================================================
    VAL_MISSING_FIELD         = "VAL_MISSING_FIELD"
    VAL_MISSING_REQUIRED_FIELD = "VAL_MISSING_REQUIRED_FIELD"
    VAL_INVALID_FORMAT        = "VAL_INVALID_FORMAT"
    VAL_INVALID_LENGTH        = "VAL_INVALID_LENGTH"
    VAL_INVALID_VALUE         = "VAL_INVALID_VALUE"
    VAL_FIELD_NOT_ALLOWED     = "VAL_FIELD_NOT_ALLOWED"
    VAL_INVALID_MOBILE        = "VAL_INVALID_MOBILE"
    VAL_INVALID_EMAIL         = "VAL_INVALID_EMAIL"
    VAL_INVALID_PAN           = "VAL_INVALID_PAN"
    VAL_FIELD_TOO_SHORT       = "VAL_FIELD_TOO_SHORT"
    VAL_FIELD_TOO_LONG        = "VAL_FIELD_TOO_LONG"
    VAL_INVALID_FIELD         = "VAL_INVALID_FIELD"

    # =============================================================================
    # Database / Data Layer
    # =============================================================================
    DB_QUERY_FAILED           = "DB_QUERY_FAILED"
    DB_CONSTRAINT_VIOLATION   = "DB_CONSTRAINT_VIOLATION"
    DB_RECORD_NOT_FOUND       = "DB_RECORD_NOT_FOUND"
    DB_TRANSACTION_FAILED     = "DB_TRANSACTION_FAILED"

    # =============================================================================
    # ICICI CRM Integration
    # =============================================================================
    ICICI_API_ERROR           = "ICICI_API_ERROR"
    ICICI_AUTH_FAILED         = "ICICI_AUTH_FAILED"
    ICICI_TIMEOUT             = "ICICI_TIMEOUT"
    ICICI_RATE_LIMIT          = "ICICI_RATE_LIMIT"
    ICICI_INVALID_RESPONSE    = "ICICI_INVALID_RESPONSE"
    ICICI_RETRY_EXHAUSTED     = "ICICI_RETRY_EXHAUSTED"

    # =============================================================================
    # Business Rules
    # =============================================================================
    BIZ_RULE_VIOLATION        = "BIZ_RULE_VIOLATION"
    BIZ_INVALID_STATE         = "BIZ_INVALID_STATE"
    BIZ_OPERATION_NOT_ALLOWED = "BIZ_OPERATION_NOT_ALLOWED"
    SVC_NOT_FOUND             = "SVC_NOT_FOUND"
