"""
apps/authentication/permissions.py
=====================================
Custom DRF permission classes for ICICI CRM.

Responsibilities:
  - Define reusable permission gates beyond IsAuthenticated.
  - Role-based access control (RBAC) using JWT claims.
  - Object-level permissions where needed.

Hierarchy:
  IsAuthenticated (DRF built-in)
    └── IsActiveUser          ← user.is_active check
         └── HasRole          ← role claim from JWT payload
              └── IsAdminUser ← shorthand for role == 'admin'

Usage in views:
    from rest_framework.permissions import IsAuthenticated
    from apps.authentication.permissions import IsAdminUser, HasRole

    class SomeView(APIView):
        permission_classes = [IsAuthenticated, IsAdminUser]

    class AnotherView(APIView):
        permission_classes = [IsAuthenticated, HasRole("manager")]
"""

import logging

from rest_framework import permissions

logger = logging.getLogger(__name__)


class IsActiveUser(permissions.BasePermission):
    """
    Grants access only to users with is_active=True.

    Use alongside IsAuthenticated — this adds the active check
    in case your JWTAuthentication backend doesn't filter by is_active.
    """

    message = "Your account is inactive. Contact support."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
        )


class HasRole(permissions.BasePermission):
    """
    Dynamic role-based permission class.

    Checks the 'role' claim in the decoded JWT payload (attached as request.auth).

    Usage:
        permission_classes = [IsAuthenticated, HasRole("admin")]
        permission_classes = [IsAuthenticated, HasRole("manager", "admin")]

    Args:
        *required_roles: One or more role strings. User must have at least one.
    """

    message = "You do not have the required role to access this resource."

    def __init__(self, *required_roles: str):
        self.required_roles = set(required_roles)

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        # request.auth is the decoded JWT payload dict (set by JWTAuthentication)
        payload = request.auth or {}
        user_role = payload.get("role", "")

        granted = user_role in self.required_roles
        if not granted:
            logger.warning(
                "Access denied: user_id=%s role='%s' required_roles=%s path=%s",
                getattr(request.user, "pk", "unknown"),
                user_role,
                self.required_roles,
                request.path,
            )
        return granted


class IsAdminUser(permissions.BasePermission):
    """
    Shorthand permission for admin-only endpoints.
    Equivalent to HasRole("admin").
    """

    message = "Only admin users can access this resource."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        payload = request.auth or {}
        return payload.get("role") == "admin"


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Grants access to users with role 'manager' or 'admin'.
    """

    message = "Only managers or admins can access this resource."

    ALLOWED_ROLES = {"manager", "admin"}

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        payload = request.auth or {}
        return payload.get("role") in self.ALLOWED_ROLES


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission: grants access if the requesting user owns the object,
    OR if the user has the 'admin' role.

    Requires the model to have a 'created_by' or 'owner' field pointing to User.

    Usage:
        permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    """

    message = "You do not have permission to access this object."

    def has_object_permission(self, request, view, obj) -> bool:
        payload = request.auth or {}
        if payload.get("role") == "admin":
            return True

        # Check 'created_by' or 'owner' fields
        owner = getattr(obj, "created_by", None) or getattr(obj, "owner", None)
        return owner == request.user
