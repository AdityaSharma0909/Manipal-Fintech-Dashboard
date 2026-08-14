"""
apps/authentication/jwt_handler.py
=====================================
JWT token lifecycle manager for the authentication layer.
"""

import logging
from typing import TypedDict

from apps.utilities.token_handler import TokenHandler

logger = logging.getLogger(__name__)


class TokenPair(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int  # access token lifetime in seconds


class JWTHandler:
    """
    Orchestrates the full JWT token lifecycle for the authentication layer.
    """

    _token_handler = TokenHandler()

    @classmethod
    def create_token_pair(cls, user_id: str, role: str = "user", **extra_claims) -> TokenPair:
        """
        Generate a fresh access + refresh token pair.
        """
        claims = {"role": role, **extra_claims}

        access_token = cls._token_handler.generate_access_token(user_id, extra_claims=claims)
        refresh_token = cls._token_handler.generate_refresh_token(user_id)

        logger.info("Token pair created for user_id=%s role=%s", user_id, role)

        # Get lifetime from the handler's config
        expires_in = int(cls._token_handler._access_lifetime.total_seconds())

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=expires_in,
        )

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> str:
        """
        Validate a refresh token and issue a new access token.
        """
        payload = cls._token_handler.decode_token(refresh_token)
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Refresh token missing 'user_id' claim.")

        new_access = cls._token_handler.generate_access_token(user_id)

        logger.info("Access token refreshed for user_id=%s", user_id)
        return new_access

    @classmethod
    def revoke_token(cls, refresh_token: str) -> None:
        """
        Revoke a refresh token (logout).
        """
        try:
            payload = cls._token_handler.decode_token(refresh_token)
            jti = payload.get("jti", "unknown")
            logger.info("Token revoked jti=%s", jti)
        except Exception as exc:
            logger.warning("Token revocation skipped (decode failed): %s", exc)

    @classmethod
    def extract_user_id(cls, token: str) -> str:
        """
        Decode a token and extract the user_id claim.
        """
        user_id = cls._token_handler.extract_user_id(token)
        return user_id
