"""
apps/common/exceptions/integration_exceptions.py
=================================================
Exceptions raised specifically during ICICI CRM external API integration.

Raised by: apps/integrations/icici/base_client.py
Caught by:  apps/business/services/* (then re-raised as domain exceptions)

Never let integration exceptions propagate directly to API views.
"""

from rest_framework import status
from .base_exception import CRMBaseException


class IntegrationException(CRMBaseException):
    """Base class for all external integration failures."""
    message = "An external integration error occurred."
    code = "INTEGRATION_ERROR"
    http_status = status.HTTP_502_BAD_GATEWAY


# Aliases
ICICIIntegrationException = IntegrationException


class ICICIAPIException(IntegrationException):
    """Raised when ICICI CRM API returns an error response."""
    message = "ICICI CRM API returned an error."
    code = "ICICI_API_ERROR"
    http_status = status.HTTP_502_BAD_GATEWAY


class ICICITimeoutException(IntegrationException):
    """Raised when ICICI CRM API call times out."""
    message = "ICICI CRM API request timed out."
    code = "ICICI_TIMEOUT"
    http_status = status.HTTP_504_GATEWAY_TIMEOUT


class ICICIAuthException(IntegrationException):
    """Raised when ICICI CRM API rejects authentication credentials."""
    message = "ICICI CRM API authentication failed."
    code = "ICICI_AUTH_FAILED"
    http_status = status.HTTP_401_UNAUTHORIZED


class ICICIRateLimitException(IntegrationException):
    """Raised when ICICI CRM API enforces rate limiting."""
    message = "ICICI CRM API rate limit exceeded."
    code = "ICICI_RATE_LIMIT"
    http_status = status.HTTP_429_TOO_MANY_REQUESTS


class IntegrationRetryExhaustedException(IntegrationException):
    """Raised when all retry attempts for an integration call have failed."""
    message = "Maximum retry attempts exhausted for external API call."
    code = "RETRY_EXHAUSTED"
    http_status = status.HTTP_503_SERVICE_UNAVAILABLE
