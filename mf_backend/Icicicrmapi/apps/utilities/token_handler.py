"""
apps/utilities/token_handler.py
=================================
JWT token generation, validation, and decoding utility.

Responsibilities:
  - Generate access and refresh JWT tokens for authenticated users
  - Validate and decode incoming JWT tokens
  - Extract claims (user_id, roles, etc.) from token payloads
  - Handle token expiry, signature errors cleanly

Note:
  djangorestframework-simplejwt handles token lifecycle for DRF views.
  This module provides lower-level JWT operations needed by:
    - ICICI integration auth flows
    - Custom token refresh logic
    - Inter-service token validation

Settings consumed (from settings.SIMPLE_JWT):
  JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME

Usage:
    from apps.utilities.token_handler import TokenHandler
    handler = TokenHandler()
    tokens = handler.generate_tokens(user_id="uuid-...", roles=["agent"])
    payload = handler.decode_token(tokens["access"])
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

import jwt
from django.conf import settings

from apps.common.exceptions.base_exception import UnauthorizedException
from apps.common.constants.app_constants import TokenType

logger = logging.getLogger(__name__)

_JWT_SETTINGS = lambda: settings.SIMPLE_JWT  # noqa: E731


class TokenHandler:
    """
    Low-level JWT token utility.

    For DRF view-level auth, use simplejwt's built-in views.
    Use this class for programmatic token operations.
    """

    def __init__(self):
        cfg = settings.SIMPLE_JWT
        self._secret: str = cfg.get("SIGNING_KEY") or settings.SECRET_KEY
        self._algorithm: str = cfg.get("ALGORITHM", "HS256")
        self._access_lifetime: timedelta = cfg.get("ACCESS_TOKEN_LIFETIME", timedelta(hours=1))
        self._refresh_lifetime: timedelta = cfg.get("REFRESH_TOKEN_LIFETIME", timedelta(days=7))

    # -------------------------------------------------------------------------
    # Token generation
    # -------------------------------------------------------------------------

    def generate_access_token(self, user_id: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
        """Generate a short-lived access JWT."""
        return self._build_token(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            lifetime=self._access_lifetime,
            extra_claims=extra_claims,
        )

    def generate_refresh_token(self, user_id: str) -> str:
        """Generate a long-lived refresh JWT."""
        return self._build_token(
            user_id=user_id,
            token_type=TokenType.REFRESH,
            lifetime=self._refresh_lifetime,
        )

    def generate_tokens(
        self,
        user_id: str,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Generate both access and refresh tokens in one call."""
        return {
            "access": self.generate_access_token(user_id, extra_claims=extra_claims),
            "refresh": self.generate_refresh_token(user_id),
        }

    # -------------------------------------------------------------------------
    # Token decoding / validation
    # -------------------------------------------------------------------------

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.

        Returns:
            Payload dict if valid.

        Raises:
            UnauthorizedException: If token is expired, invalid, or malformed.
        """
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"verify_exp": True},
            )
            return payload
        except jwt.ExpiredSignatureError as exc:
            logger.warning("JWT token expired.")
            raise UnauthorizedException("Token has expired. Please refresh.") from exc
        except jwt.InvalidTokenError as exc:
            logger.warning("Invalid JWT token: %s", str(exc))
            raise UnauthorizedException("Invalid token.") from exc

    def extract_user_id(self, token: str) -> str:
        """Decode token and return the user_id claim."""
        payload = self.decode_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise UnauthorizedException("Token does not contain a valid user identity.")
        return user_id

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _build_token(
        self,
        user_id: str,
        token_type: TokenType,
        lifetime: timedelta,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        now = datetime.now(tz=timezone.utc)
        payload = {
            "user_id": str(user_id),
            "token_type": token_type.value,
            "iat": now,
            "exp": now + lifetime,
        }
        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(payload, self._secret, algorithm=self._algorithm)
