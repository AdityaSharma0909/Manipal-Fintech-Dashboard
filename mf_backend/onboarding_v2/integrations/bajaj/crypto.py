
from __future__ import annotations
import os
import base64
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

from .exceptions import BajajConfigurationError, BajajRequestError

logger = logging.getLogger(__name__)


def _sanitize_iv(iv_str: str) -> str:
    return iv_str.strip().strip("\x00").strip()


def _sanitize_key(key_str: str) -> str:
    return key_str.strip().strip("\x00").strip()


def _validate_encryption_params(key_str: str, iv_str: str):
    sanitized_key = _sanitize_key(key_str)
    sanitized_iv = _sanitize_iv(iv_str)

    logger.info(f"AES Key Length: {len(sanitized_key)}")
    logger.info(f"IV Length: {len(sanitized_iv)}")
    logger.info(f"IV Value: {sanitized_iv}")

    if not sanitized_key:
        raise BajajConfigurationError("Encryption key is empty after sanitization")
    if len(sanitized_key) != 32:
        raise BajajConfigurationError(
            f"Key must be exactly 32 characters. "
            f"Current length: {len(sanitized_key)}. "
            f"Check BAJAJ_SHARED_SECRET_KEY in environment."
        )
    if not sanitized_iv:
        raise BajajConfigurationError("IV is empty after sanitization")
    if len(sanitized_iv) != 16:
        raise BajajConfigurationError(
            f"IV must be exactly 16 characters. "
            f"Current length: {len(sanitized_iv)}. "
            f"IV value: '{sanitized_iv}'. "
            f"Check BAJAJ_SHARED_SECRET_IV in environment for special characters "
            f"(especially # which is parsed as comment by django-environ). "
            f"If the IV contains #, wrap the value in double quotes in .env file."
        )

    return sanitized_key, sanitized_iv


class AESCryptoUtility:
    """
    Uses AES-256-CBC with PKCS7 padding.
    """

    @staticmethod
    def encrypt(plain_text: str, key_str: str, iv_str: str) -> str:
        if not plain_text:
            raise ValueError("plain_text is required")

        sanitized_key, sanitized_iv = _validate_encryption_params(key_str, iv_str)
        try:
            key = sanitized_key.encode("utf-8")
            iv = sanitized_iv.encode("utf-8")

            # PKCS7 padding
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(plain_text.encode("utf-8")) + padder.finalize()
            # Cipher construction
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
            return base64.b64encode(encrypted_bytes).decode("utf-8")
        except Exception as ex:
            logger.error(f"AES Encrypt failed: {str(ex)}")
            raise BajajRequestError(f"AES Encrypt failed: {str(ex)}")

    @staticmethod
    def decrypt(cipher_text: str, key_str: str, iv_str: str) -> str:
        if not cipher_text:
            raise ValueError("cipher_text is required")

        sanitized_key, sanitized_iv = _validate_encryption_params(key_str, iv_str)
        try:
            key = sanitized_key.encode("utf-8")
            iv = sanitized_iv.encode("utf-8")

            encrypted_data = base64.b64decode(cipher_text)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
            # Unpadding
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            plain_data = unpadder.update(decrypted_padded) + unpadder.finalize()

            return plain_data.decode("utf-8")
        except Exception as ex:
            logger.error(f"AES Decrypt failed: {str(ex)}")
            raise BajajRequestError(f"AES Decrypt failed: {str(ex)}")

