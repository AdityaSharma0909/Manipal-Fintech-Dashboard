import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class AuthEncryptionService:
    """
    Encryption service for internal authentication tokens (Gold Loan API integration).
    Uses TripleDES (3DES) in ECB mode with PKCS7 padding.
    """

    @staticmethod
    def decrypt_auth_token(encrypted_data: str, key_str: str) -> str:
        """
        Decrypts an authentication claim (Role/Username) using 3DES.
        """
        if not encrypted_data:
            return ""

        try:
            # Decode from Base64
            input_bytes = base64.b64decode(encrypted_data)
            
            # Key must be exactly 16 or 24 bytes for 3DES
            key_bytes = key_str.encode("utf-8")
            
            # Initialize 3DES in ECB mode
            cipher = Cipher(algorithms.TripleDES(key_bytes), modes.ECB(), backend=default_backend())
            decryptor = cipher.decryptor()
            
            # Decrypt
            decrypted_padded = decryptor.update(input_bytes) + decryptor.finalize()
            
            # PKCS7 Unpadding
            unpadder = padding.PKCS7(64).unpadder() # 3DES block size is 64 bits
            decrypted_bytes = unpadder.update(decrypted_padded) + unpadder.finalize()
            
            return decrypted_bytes.decode("utf-8")
        except Exception:
            return ""
