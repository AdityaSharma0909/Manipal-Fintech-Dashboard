"""
apps/utilities/encryption.py
==============================
Symmetric encryption/decryption utility using Fernet (AES-128-CBC + HMAC).

Use cases:
  - Encrypting sensitive fields before storage (PAN, Aadhaar, etc.)
  - Encrypting payloads sent to ICICI CRM API
  - Decrypting values returned from ICICI CRM API

Key management:
  - ENCRYPTION_KEY must be a 32-byte URL-safe base64-encoded string
  - Set in .env as ENCRYPTION_KEY
  - Generated with: from cryptography.fernet import Fernet; Fernet.generate_key()

Usage:
    from apps.utilities.encryption import EncryptionService
    svc = EncryptionService()
    encrypted = svc.encrypt("sensitive-data")
    original  = svc.decrypt(encrypted)
"""

import base64
import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from apps.common.exceptions.base_exception import CRMBaseException

logger = logging.getLogger(__name__)


class EncryptionError(CRMBaseException):
    message = "Encryption/decryption operation failed."
    code = "ENCRYPTION_ERROR"


class EncryptionService:
    """
    Fernet-based symmetric encryption service.

    Thread-safe: Fernet instances are stateless after initialization.
    Instantiate once (as singleton or per-request) — both are safe.
    """

    def __init__(self, key: Optional[str] = None):
        raw_key = key or settings.ENCRYPTION_KEY
        if not raw_key:
            raise EncryptionError("ENCRYPTION_KEY is not configured in settings.")
        try:
            self._fernet = Fernet(raw_key.encode() if isinstance(raw_key, str) else raw_key)
        except Exception as exc:
            logger.error("Failed to initialize Fernet with the provided key: %s", exc)
            raise EncryptionError("Invalid ENCRYPTION_KEY format.") from exc

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.

        Args:
            plaintext: The string to encrypt.

        Returns:
            URL-safe base64-encoded ciphertext string.

        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode("utf-8"))
            return encrypted_bytes.decode("utf-8")
        except Exception as exc:
            logger.error("Encryption failed: %s", exc)
            raise EncryptionError("Failed to encrypt the provided value.") from exc

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a Fernet-encrypted ciphertext string.

        Args:
            ciphertext: The encrypted string (output of encrypt()).

        Returns:
            Original plaintext string.

        Raises:
            EncryptionError: If decryption fails (tampered data, wrong key, expired token).
        """
        try:
            decrypted_bytes = self._fernet.decrypt(ciphertext.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken as exc:
            logger.warning("Decryption failed — invalid or tampered token.")
            raise EncryptionError("Decryption failed: token is invalid or has been tampered.") from exc
        except Exception as exc:
            logger.error("Decryption error: %s", exc)
            raise EncryptionError("Failed to decrypt the provided value.") from exc

    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt raw bytes. Returns encrypted bytes."""
        try:
            return self._fernet.encrypt(data)
        except Exception as exc:
            raise EncryptionError("Failed to encrypt bytes.") from exc

    def decrypt_bytes(self, data: bytes) -> bytes:
        """Decrypt raw bytes. Returns decrypted bytes."""
        try:
            return self._fernet.decrypt(data)
        except InvalidToken as exc:
            raise EncryptionError("Decryption of bytes failed: invalid token.") from exc
