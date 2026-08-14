from __future__ import annotations

from dataclasses import dataclass

from jwcrypto import jwk, jwe, jws

from .exceptions import AxisConfigurationError, AxisIntegrationError


def _read_pem_file(path: str) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError as exc:
        raise AxisConfigurationError(f"Key file not found: {path}") from exc


@dataclass(frozen=True)
class AxisJoseKeys:
    axis_encrypt_public: jwk.JWK
    partner_sign_private: jwk.JWK
    partner_decrypt_private: jwk.JWK
    axis_verify_public: jwk.JWK


def load_jose_keys(
    *,
    axis_encrypt_public_key_pem_file: str,
    partner_sign_private_key_pem_file: str,
    partner_decrypt_private_key_pem_file: str | None = None,
    axis_verify_public_key_pem_file: str | None = None,
) -> AxisJoseKeys:
    axis_encrypt_public = jwk.JWK.from_pem(_read_pem_file(axis_encrypt_public_key_pem_file))
    partner_sign_private = jwk.JWK.from_pem(_read_pem_file(partner_sign_private_key_pem_file))

    # Default decrypt/verify keys to same as encrypt/sign counterparts.
    partner_decrypt_private = (
        jwk.JWK.from_pem(_read_pem_file(partner_decrypt_private_key_pem_file))
        if partner_decrypt_private_key_pem_file
        else partner_sign_private
    )
    axis_verify_public = (
        jwk.JWK.from_pem(_read_pem_file(axis_verify_public_key_pem_file))
        if axis_verify_public_key_pem_file
        else axis_encrypt_public
    )

    return AxisJoseKeys(
        axis_encrypt_public=axis_encrypt_public,
        partner_sign_private=partner_sign_private,
        partner_decrypt_private=partner_decrypt_private,
        axis_verify_public=axis_verify_public,
    )


def encrypt_and_sign(*, keys: AxisJoseKeys, payload_json: str) -> str:
    """
    Axis scheme (per docs): JWE encrypt (RSA-OAEP-256 + A256GCM) then JWS sign (RS256) of the JWE compact string.
    Returns compact JWS string (what we send as HTTP body with Content-Type text/plain).
    """
    jwe_token = jwe.JWE(
        plaintext=payload_json.encode("utf-8"),
        protected={"alg": "RSA-OAEP-256", "enc": "A256GCM"},
    )
    jwe_token.add_recipient(keys.axis_encrypt_public)
    jwe_compact = jwe_token.serialize(compact=True)

    signed = jws.JWS(jwe_compact.encode("utf-8"))
    signed.add_signature(keys.partner_sign_private, None, {"alg": "RS256"}, None)
    return signed.serialize(compact=True)


def verify_and_decrypt(*, keys: AxisJoseKeys, token: str) -> str:
    """
    Verify RS256 JWS and decrypt inner JWE payload.
    Returns decrypted plaintext JSON string.
    """
    try:
        signed = jws.JWS()
        signed.deserialize(token)
        signed.verify(keys.axis_verify_public)
        inner = signed.payload.decode("utf-8")

        encrypted = jwe.JWE()
        encrypted.deserialize(inner)
        encrypted.decrypt(keys.partner_decrypt_private)
        return encrypted.payload.decode("utf-8")
    except Exception as exc:
        raise AxisIntegrationError("Failed to verify/decrypt Axis payload") from exc

