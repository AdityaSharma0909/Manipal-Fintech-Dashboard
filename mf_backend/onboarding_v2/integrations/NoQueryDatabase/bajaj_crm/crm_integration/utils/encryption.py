import os
import base64
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from django.conf import settings

logger = logging.getLogger(__name__)

BYPASS_ENCRYPTION = os.environ.get('BYPASS_ENCRYPTION', 'false').lower() == 'true'

if BYPASS_ENCRYPTION:
    logger.warning("BYPASS_ENCRYPTION is ENABLED - all encryption will be skipped")


def _sanitize_iv(iv_str: str) -> str:
    return iv_str.strip().strip('\x00').strip()


def _sanitize_key(key_str: str) -> str:
    return key_str.strip().strip('\x00').strip()


def _validate_encryption_params(key_str: str, iv_str: str):
    sanitized_key = _sanitize_key(key_str)
    sanitized_iv = _sanitize_iv(iv_str)

    logger.info(f"AES Key Length: {len(sanitized_key)}")
    logger.info(f"IV Length: {len(sanitized_iv)}")
    logger.info(f"IV Value: {sanitized_iv}")
    logger.info(f"Encryption About To Start")

    if not sanitized_key:
        raise ValueError("Encryption key is empty after sanitization")
    if len(sanitized_key) != 32:
        raise ValueError(
            f"Key must be exactly 32 characters. "
            f"Current length: {len(sanitized_key)}. "
            f"Check BAJAJ_SHARED_SECRET_KEY in environment."
        )
    if not sanitized_iv:
        raise ValueError("IV is empty after sanitization")
    if len(sanitized_iv) != 16:
        raise ValueError(
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
            key = sanitized_key.encode('utf-8')
            iv = sanitized_iv.encode('utf-8')
            
            # PKCS7 padding
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()
            
            # Cipher construction
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
            
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as ex:
            logger.error(f"AES Encrypt failed: {str(ex)}")
            raise

    @staticmethod
    def decrypt(cipher_text: str, key_str: str, iv_str: str) -> str:
        if not cipher_text:
            raise ValueError("cipher_text is required")
        
        sanitized_key, sanitized_iv = _validate_encryption_params(key_str, iv_str)
            
        try:
            key = sanitized_key.encode('utf-8')
            iv = sanitized_iv.encode('utf-8')
            
            encrypted_data = base64.b64decode(cipher_text)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Unpadding
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            plain_data = unpadder.update(decrypted_padded) + unpadder.finalize()
            
            return plain_data.decode('utf-8')
        except Exception as ex:
            logger.error(f"AES Decrypt failed: {str(ex)}")
            raise


class GoldLoanEncryptionService:
    """

    Performs TripleDES-ECB and AES-CBC decryption for gold loan user tokens/roles.
    """
    
    @staticmethod
    def _read_key_from_file() -> str:
        key_path = settings.KEYS.get('KEY_PATH')
        if not key_path:
            raise ValueError("KEYS_KEY_PATH is not configured in settings.")
            
        try:
            with open(key_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as ex:
            logger.error(f"Failed to read key from path {key_path}: {str(ex)}")
            raise

    @classmethod
    def encrypt_triple_des(cls, plain_text: str) -> str:
        try:
            key_str = cls._read_key_from_file()
            key = key_str.encode('utf-8')
            # TripleDES key size must be 24 bytes (192 bits)
            key = key[:24].ljust(24, b'\0')
            
            padder = padding.PKCS7(algorithms.TripleDES.block_size).padder()
            padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()
            
            cipher = Cipher(algorithms.TripleDES(key), modes.ECB())
            encryptor = cipher.encryptor()
            encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
            
            return base64.b64encode(encrypted_bytes).decode('utf-8')
        except Exception as ex:
            logger.error(f"TripleDES Encrypt failed: {str(ex)}")
            return ""

    @classmethod
    def decrypt_triple_des(cls, cipher_text: str) -> str:
        if not cipher_text or cipher_text.upper() == "YES":
            return ""
            
        try:
            key_str = cls._read_key_from_file()
            key = key_str.encode('utf-8')
            key = key[:24].ljust(24, b'\0')
            
            encrypted_data = base64.b64decode(cipher_text)
            cipher = Cipher(algorithms.TripleDES(key), modes.ECB())
            decryptor = cipher.decryptor()
            decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
            
            unpadder = padding.PKCS7(algorithms.TripleDES.block_size).unpadder()
            plain_data = unpadder.update(decrypted_padded) + unpadder.finalize()
            
            return plain_data.decode('utf-8')
        except Exception as ex:
            logger.error(f"TripleDES Decrypt failed: {str(ex)}")
            return ""

    @staticmethod
    def decrypt_aes_cbc_zero_iv(encrypted_text: str) -> str:
        """Decryption method using AES-256-CBC and static zero IV."""
        if not encrypted_text:
            return ""
            
        try:
            secret_key = settings.KEYS.get('DECRYPT_KEY', '')
            # C# padding: secretKey.PadRight(32).Substring(0, 32)
            key = secret_key.ljust(32)[:32].encode('utf-8')
            iv = b'\0' * 16
            
            encrypted_data = base64.b64decode(encrypted_text)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
            
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            plain_data = unpadder.update(decrypted_padded) + unpadder.finalize()
            
            return plain_data.decode('utf-8')
        except Exception as ex:
            logger.error(f"Zero IV AES Decrypt failed: {str(ex)}")
            return ""
