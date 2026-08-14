# apps.authentication — JWT authentication layer.
#
# Exports:
#   DelegatedJWTAuthentication → authentication backend (use in DRF DEFAULT_AUTHENTICATION_CLASSES)
#   JWTHandler                 → token lifecycle: create, refresh, revoke
#   IsAdminUser                → permission class shorthand

from apps.authentication.backends import DelegatedJWTAuthentication
from apps.authentication.jwt_handler import JWTHandler
from apps.authentication.permissions import (
    IsActiveUser,
    IsAdminUser,
    IsManagerOrAdmin,
    IsOwnerOrAdmin,
    HasRole,
)

__all__ = [
    "DelegatedJWTAuthentication",
    "JWTHandler",
    "IsActiveUser",
    "IsAdminUser",
    "IsManagerOrAdmin",
    "IsOwnerOrAdmin",
    "HasRole",
]
