import hmac
import hashlib
import base64


def generate_hmac_signature(
    method: str,
    api_endpoint: str,
    timestamp: str,
    nonce: str,
    request_body: str,
    secret_key: str
) -> str:
    """Generates an HMAC SHA256 signature matching the C# implementation.

    1. Computes the SHA256 hash of the request body as a lowercase hex string.
    2. Builds a canonical string by joining fields with newlines.
    3. Hashes the canonical string using HMAC-SHA256 with the secret key.
    4. Returns the base64-encoded signature.
    """
    # 1. SHA256 hash of request body
    body_hash_bytes = hashlib.sha256(request_body.encode('utf-8')).digest()
    body_hash = body_hash_bytes.hex().lower()

    # 2. Canonical string
    canonical = "\n".join([
        method.upper(),
        api_endpoint,
        timestamp,
        nonce,
        body_hash
    ])

    # 3. HMAC SHA256
    key_bytes = secret_key.encode('utf-8')
    hmac_obj = hmac.new(key_bytes, canonical.encode('utf-8'), hashlib.sha256)
    signature_bytes = hmac_obj.digest()

    # 4. Base64 encode
    return base64.b64encode(signature_bytes).decode('utf-8')
