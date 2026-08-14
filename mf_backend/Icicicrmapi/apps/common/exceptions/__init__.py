# apps.common.exceptions — Centralised exception hierarchy.
#
# Usage:
#   from apps.common.exceptions import NotFoundException, ValidationException

from apps.common.exceptions.base_exception import (
    CRMBaseException,
    ValidationException,
    NotFoundException,
    ConflictException,
    AuthenticationException,
    AuthorizationException,
    BusinessRuleException,
    ServiceUnavailableException,
    crm_exception_handler,
)
from apps.common.exceptions.http_exceptions import (
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException as NotFoundHTTPException,
    MethodNotAllowedException,
    TooManyRequestsException,
)
from apps.common.exceptions.integration_exceptions import (
    ICICIIntegrationException,
    ICICIAuthException,
    ICICITimeoutException,
    ICICIRateLimitException,
)

__all__ = [
    "CRMBaseException",
    "ValidationException",
    "NotFoundException",
    "ConflictException",
    "AuthenticationException",
    "AuthorizationException",
    "BusinessRuleException",
    "ServiceUnavailableException",
    "crm_exception_handler",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundHTTPException",
    "MethodNotAllowedException",
    "TooManyRequestsException",
    "ICICIIntegrationException",
    "ICICIAuthException",
    "ICICITimeoutException",
    "ICICIRateLimitException",
]
