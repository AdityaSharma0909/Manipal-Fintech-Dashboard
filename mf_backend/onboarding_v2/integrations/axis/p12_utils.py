from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from .exceptions import AxisConfigurationError


def load_pkcs12_cert_and_key(
    pkcs12_path: str,
    password: Optional[str],
) -> Tuple[bytes, bytes]:
    """
  Load client certificate and private key PEM bytes from a .p12 / .pfx file.
  """
    path = Path(pkcs12_path)
    if not path.is_file():
        raise AxisConfigurationError(f"PKCS12 file not found: {pkcs12_path}")

    pwd: Optional[bytes] = None
    if password is not None and str(password).strip() != "":
        pwd = str(password).encode("utf-8")

    try:
        private_key, certificate, _additional = pkcs12.load_key_and_certificates(
            path.read_bytes(),
            pwd,
            default_backend(),
        )
    except Exception as exc:
        raise AxisConfigurationError(
            f"Failed to load PKCS12 ({pkcs12_path}). Check path and AXIS_*_MTLS_PKCS12_PASSWORD."
        ) from exc

    if private_key is None or certificate is None:
        raise AxisConfigurationError(
            f"PKCS12 ({pkcs12_path}) must contain both a client certificate and private key."
        )

    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    cert_pem = certificate.public_bytes(encoding=serialization.Encoding.PEM)
    return cert_pem, key_pem
