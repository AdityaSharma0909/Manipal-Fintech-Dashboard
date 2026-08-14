import base64
import os
import secrets
from typing import Tuple, Any
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives.serialization import pkcs12


class ICICIEncryptionService:
    """
    Asymmetric (RSA) and Symmetric (AES) encryption service tailored for ICICI CRM API.
    """
    _public_key_cache = {}
    _private_key_cache = {}

    @classmethod
    def encrypt_payload(cls, payload_json: str, public_key_path: str) -> Tuple[str, str]:
        """
        Encrypts payload using RSA-OAEP for session key and AES-CBC for data.
        Returns (encrypted_key, encrypted_data).
        """
        # 1. Generate a 16-byte random session key
        session_key = secrets.token_bytes(16)
        
        # 2. Encrypt session key with RSA Public Key
        if public_key_path not in cls._public_key_cache:
            with open(public_key_path, "rb") as key_file:
                key_data = key_file.read()
                
            public_key = None
            try:
                cert = x509.load_pem_x509_certificate(key_data, default_backend())
                public_key = cert.public_key()
            except ValueError:
                try:
                    cert = x509.load_der_x509_certificate(key_data, default_backend())
                    public_key = cert.public_key()
                except ValueError:
                    try:
                        public_key = serialization.load_pem_public_key(key_data, backend=default_backend())
                    except ValueError:
                        public_key = serialization.load_der_public_key(key_data, backend=default_backend())
            cls._public_key_cache[public_key_path] = public_key
            
        public_key = cls._public_key_cache[public_key_path]
            
        encrypted_key_bytes = public_key.encrypt(
            session_key,
            asym_padding.PKCS1v15() # Matching RSAEncryptionPadding.Pkcs1
        )
        encrypted_key_b64 = base64.b64encode(encrypted_key_bytes).decode("utf-8")
        
        # 3. Encrypt data with AES-CBC
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # PKCS7 Padding
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(payload_json.encode("utf-8")) + padder.finalize()
        
        encrypted_data_bytes = encryptor.update(padded_data) + encryptor.finalize()
        
        # Prepend IV (matching implementation: ms.Write(iv, 0, iv.Length))
        final_encrypted_data = base64.b64encode(iv + encrypted_data_bytes).decode("utf-8")
        
        return encrypted_key_b64, final_encrypted_data

    @classmethod
    def decrypt_payload(cls, encrypted_data_b64: str, encrypted_key_b64: str, pfx_path: str, pfx_password: str) -> str:
        """
        Decrypts payload using RSA for session key and AES-CBC for data.
        """
        # 1. Decrypt Session Key using Private Key from PFX
        cache_key = f"{pfx_path}_{pfx_password}"
        if cache_key not in cls._private_key_cache:
            with open(pfx_path, "rb") as key_file:
                key_data = key_file.read()
                
            try:
                private_key, _, _ = pkcs12.load_key_and_certificates(
                    key_data,
                    pfx_password.encode() if pfx_password else None,
                    backend=default_backend()
                )
            except ValueError:
                # Fallback if it's a raw PEM private key
                private_key = serialization.load_pem_private_key(
                    key_data,
                    password=pfx_password.encode() if pfx_password else None,
                    backend=default_backend()
                )
            cls._private_key_cache[cache_key] = private_key
            
        private_key = cls._private_key_cache[cache_key]
            
        encrypted_key_bytes = base64.b64decode(encrypted_key_b64)
        session_key = private_key.decrypt(
            encrypted_key_bytes,
            asym_padding.PKCS1v15()
        )
        
        # 2. Decrypt Data using AES-CBC
        full_data_bytes = base64.b64decode(encrypted_data_b64)
        iv = full_data_bytes[:16]
        ciphertext = full_data_bytes[16:]
        
        cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # PKCS7 Unpadding
        unpadder = padding.PKCS7(128).unpadder()
        plain_data = unpadder.update(padded_data) + unpadder.finalize()
        
        return plain_data.decode("utf-8")
