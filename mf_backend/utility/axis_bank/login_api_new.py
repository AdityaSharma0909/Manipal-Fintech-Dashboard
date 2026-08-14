import base64
import json
from base64 import urlsafe_b64encode
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import jwt
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

if __name__=='__main__':
    # Generate a random symmetric key for content encryption
    content_key = os.urandom(32)

    # Your JSON data to be encrypted
    json_data = {"example": "data"}

    # Serialize JSON data
    serialized_json_data = json.dumps(json_data).encode("utf-8")

    # Generate RSA key pair (public and private keys)
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    public_key = private_key.public_key()

    # Encrypt the content key using RSA-OAEP-256
    encrypted_content_key = public_key.encrypt(
        content_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Encrypt the JSON data using AES-GCM with the content key
    cipher = Cipher(algorithms.AES(content_key), modes.GCM(initialization_vector=os.urandom(12)), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(serialized_json_data) + encryptor.finalize()

    # Sign the ciphertext with the private key
    signature = private_key.sign(
        ciphertext,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Combine the encrypted content key, encrypted JSON data, and the signature into the final JWT
    final_jwt = encrypted_content_key + b'.' + ciphertext + b'.' + signature

    print(final_jwt)  # Assuming it's binary data; use "utf-8" if appropriate
    base64url_final_jwt = base64.urlsafe_b64encode(final_jwt).decode("utf-8")

    print(base64url_final_jwt)
