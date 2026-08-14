import uuid
from urllib.parse import urljoin
from datetime import timedelta
from typing import Optional

from minio import Minio
from minio.error import S3Error

from utils.envSetup import environment


DEFAULT_PRESIGNED_GET_EXPIRY_HOURS = 24
MAX_PRESIGNED_GET_EXPIRY_HOURS = 24 * 7


def _resolve_bucket_name():
    """
    Pick per-environment bucket name. Falls back to STORAGE_BUCKET_NAME if set,
    otherwise DEV/PROD buckets.
    """
    if environment.STORAGE_BUCKET_NAME:
        return environment.STORAGE_BUCKET_NAME
    if environment.APP_ENV and environment.APP_ENV.upper() == "DEV":
        return environment.DEV_STORAGE_BUCKET_NAME
    return environment.PROD_STORAGE_BUCKET_NAME


def _storage_secure() -> bool:
    """
    Prefer explicit env control; otherwise default to HTTPS for non-local endpoints.
    """
    raw_value = getattr(environment, "STORAGE_USE_SSL", None)
    if raw_value is not None:
        return str(raw_value).strip().lower() in {"1", "true", "yes", "on"}

    endpoint = (environment.STORAGE_ENDPOINT or "").strip().lower()
    return not (
        endpoint.startswith("localhost")
        or endpoint.startswith("127.0.0.1")
        or endpoint.startswith("host.docker.internal")
    )


def _storage_scheme() -> str:
    return "https" if _storage_secure() else "http"


def _resolve_presigned_get_expiry() -> timedelta:
    raw_value = getattr(environment, "STORAGE_PRESIGNED_GET_EXPIRY_HOURS", None)
    try:
        hours = int(raw_value) if raw_value else DEFAULT_PRESIGNED_GET_EXPIRY_HOURS
    except (TypeError, ValueError):
        hours = DEFAULT_PRESIGNED_GET_EXPIRY_HOURS

    hours = max(1, min(hours, MAX_PRESIGNED_GET_EXPIRY_HOURS))
    return timedelta(hours=hours)


def get_minio_client():
    """
    Construct a MinIO client from env.
    """
    return Minio(
        endpoint=environment.STORAGE_ENDPOINT,
        access_key=environment.STORAGE_ACCESS_KEY,
        secret_key=environment.STORAGE_SECRET_KEY,
        secure=_storage_secure(),
    )


def ensure_bucket(client: Minio, bucket: str):
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
    except S3Error:
        # If concurrent creation or already exists, ignore
        pass


def _resolve_extension(filename: Optional[str], content_type: Optional[str]) -> str:
    if filename and "." in filename:
        return "." + filename.split(".")[-1]
    if content_type:
        if "pdf" in content_type:
            return ".pdf"
        if "png" in content_type:
            return ".png"
    return ".jpg"


def _resolve_doc_code(document_type: str, subtype: Optional[str]) -> str:
    dt = (document_type or "").upper()
    sub = (subtype or "").lower()

    def _normalize_subtype(value: str) -> str:
        cleaned = "".join(ch if ch.isalnum() else "_" for ch in value.upper())
        cleaned = "_".join(part for part in cleaned.split("_") if part)
        return cleaned or "OTHER"

    if dt == "PAN":
        if "front" in sub:
            return "PAN_CARD_FRONT"
        if "back" in sub:
            return "PAN_CARD_BACK"
        return "PAN_CARD_BACK"
    if dt == "AADHAAR":
        if "front" in sub:
            return "AADHAR_CARD_FRONT"
        if "back" in sub:
            return "AADHAR_CARD_BACK"
        return "AADHAR_CARD_FRONT"
    if dt == "VOTER_ID":
        if "front" in sub:
            return "VOTER_CARD_FRONT"
        if "back" in sub:
            return "VOTER_CARD_BACK"
        return "VOTER_CARD"
    if dt == "DRIVING_LICENSE":
        if "front" in sub:
            return "DRIVING_LICENCE_FRONT"
        if "back" in sub:
            return "DRIVING_LICENCE_BACK"
        return "DRIVING_LICENCE_FRONT"
    if dt == "PASSPORT":
        if "front" in sub:
            return "PASSPORT_FRONT"
        if "back" in sub:
            return "PASSPORT_BACK"
        return "PASSPORT_FRONT"
    if dt == "SELFIE":
        return "SELFIE"
    if dt == "FRESH_LOAN":
        if "additional" in sub:
            return "FRESH_LOAN_ADDITIONAL"
        return "FRESH_LOAN"
    if dt == "OTHER":
        # Accept explicit SAAS doc codes in subtype
        saas_codes = {
            "BROADBAND_INTERNET_BILL",
            "ELECTRICITY_BILL",
            "LANDLINE_TELEPHONE_BILL",
            "LETTER_BANK_MANAGER",
            "LETTER_GAZETTED_OFFICER",
            "NOTARISED_ADDRESS_DECLARATION",
            "PASSBOOK_LATEST_ENTRIES",
            "PIPED_GAS_BILL",
            "POSSESSION_LETTER",
            "PROPERTY_TAX_RECEIPT",
            "REGISTERED_SALE_DEED",
            "UTILITY_BILL",
            "WATER_BILL",
            "BACK",
        }
        if "form60" in sub:
            return "FORM_60"
        if "application_form" in sub:
            return "APPLICATION_FORM"
        if "bank_statement" in sub:
            return "BANK_STATEMENT"
        if "rent_agreement" in sub:
            return "RENT_AGREEMENT"
        if "utility_bill" in sub:
            return "UTILITY_BILL"
        if "bureau" in sub:
            return "BUREAU_REPORT"
        if "other_kyc" in sub:
            return "OTHER_KYC"
        if sub:
            normalized = _normalize_subtype(sub)
            if normalized in saas_codes:
                return normalized
            return normalized
    if sub:
        return _normalize_subtype(sub)
    return dt


JEWELLERY_CODE_MAP = {
    "NR": "NR",
    "RING": "RN",
    "RN": "RN",
    "WC": "WC",
    "WAIST CHAIN": "WC",
    "AK": "AK",
    "ANKLET": "AK",
    "BC": "BC",
    "BALLY CHAIN": "BC",
    "BN": "BN",
    "BANGLE": "BN",
    "BANGLES": "BN",
    "BR": "BR",
    "BRACELET": "BR",
    "CH": "CH",
    "CHAIN": "CH",
    "CL": "CL",
    "CHAIN WITH LOCKET": "CL",
    "ER": "ER",
    "EARRING": "ER",
    "EARRINGS": "ER",
    "FO": "FO",
    "FOREHEAD ORNAMENT": "FO",
    "FR": "FR",
    "FINGER RING": "FR",
    "GS": "GS",
    "GEMSTONE": "GS",
    "HO": "HO",
    "HAIR ORNAMENT": "HO",
    "LC": "LC",
    "LONG CHAIN": "LC",
    "MK": "MK",
    "MENS KADA": "MK",
    "NL": "NL",
    "NECKLACE": "NL",
    "PE": "PE",
    "PENDANT": "PE",
}


def generate_jewellery_presigned_upload(
    application_id: str,
    code: str,
    side: str,
    index: int,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
):
    """
    Presign a jewellery image upload with SAAS-friendly naming.
    """
    client = get_minio_client()
    bucket = _resolve_bucket_name()
    ensure_bucket(client, bucket)

    ext = _resolve_extension(filename, content_type)
    safe_code = JEWELLERY_CODE_MAP.get(code.upper(), code.upper())
    side = side.upper()
    safe_name = f"{safe_code}_{side}_{index}{ext}"
    object_name = f"manipal/{application_id}/jewellery/{safe_name}"
    upload_url = client.presigned_put_object(bucket, object_name, expires=timedelta(minutes=15))

    scheme = _storage_scheme()
    base = f"{scheme}://{environment.STORAGE_ENDPOINT}/"
    object_url = urljoin(base, f"{bucket}/{object_name}")

    return {
        "bucket": bucket,
        "object_name": object_name,
        "upload_url": upload_url,
        "object_url": object_url,
        "headers": {"Content-Type": content_type} if content_type else {},
    }


def generate_presigned_upload(
    application_id: str,
    document_type: str,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
    subtype: Optional[str] = None,
):
    """
    Create a presigned PUT URL and a canonical object URL for mobile uploads.
    """
    client = get_minio_client()
    bucket = _resolve_bucket_name()
    ensure_bucket(client, bucket)

    ext = _resolve_extension(filename, content_type)
    code = _resolve_doc_code(document_type, subtype)
    unique_id = uuid.uuid4().hex[:8]
    safe_name = f"{code}_{unique_id}{ext}"
    object_name = f"{environment.APP_ENV.lower() if environment.APP_ENV else 'env'}/manipal/{application_id}/{document_type.lower()}/{safe_name}"
    upload_url = client.presigned_put_object(bucket, object_name, expires=timedelta(minutes=15))

    # Form a simple object URL; for MinIO gateway format.
    scheme = _storage_scheme()
    base = f"{scheme}://{environment.STORAGE_ENDPOINT}/"
    object_url = urljoin(base, f"{bucket}/{object_name}")

    return {
        "bucket": bucket,
        "object_name": object_name,
        "upload_url": upload_url,
        "object_url": object_url,
        "headers": {"Content-Type": content_type} if content_type else {},
    }


def generate_presigned_get(
    file_url: Optional[str] = None,
    object_name: Optional[str] = None,
    response_headers: Optional[dict] = None,
):
    """
    Create a presigned GET URL for an existing object. Accepts either a full file_url or the object_name key.
    """
    client = get_minio_client()
    bucket = _resolve_bucket_name()
    ensure_bucket(client, bucket)

    # Derive object_name from file_url if not provided
    if not object_name and file_url:
        # Expect formats like http://endpoint/bucket/object/path
        from urllib.parse import urlparse

        parsed = urlparse(file_url)
        path = parsed.path.lstrip("/")
        parts = path.split("/", 1)
        if len(parts) == 2 and parts[0] == bucket:
            object_name = parts[1]
        else:
            object_name = path

    if not object_name:
        raise ValueError("object_name or file_url is required")

    expires = _resolve_presigned_get_expiry()
    get_url = client.presigned_get_object(
        bucket,
        object_name,
        expires=expires,
        response_headers=response_headers,
    )
    return {
        "bucket": bucket,
        "object_name": object_name,
        "get_url": get_url,
        "expires_in_seconds": int(expires.total_seconds()),
    }


def upload_to_storage(
    application_id: str,
    document_type: str,
    content: bytes,
    filename: Optional[str] = None,
    content_type: Optional[str] = "application/pdf",
    subtype: Optional[str] = None,
):
    """
    Directly upload content to storage and return the canonical object URL.
    """
    import io

    client = get_minio_client()
    bucket = _resolve_bucket_name()
    ensure_bucket(client, bucket)

    ext = _resolve_extension(filename, content_type)
    code = _resolve_doc_code(document_type, subtype)
    unique_id = uuid.uuid4().hex[:8]
    safe_name = f"{code}_{unique_id}{ext}"
    object_name = f"{environment.APP_ENV.lower() if environment.APP_ENV else 'env'}/manipal/{application_id}/{document_type.lower()}/{safe_name}"

    data_stream = io.BytesIO(content)
    client.put_object(bucket, object_name, data_stream, len(content), content_type=content_type)

    scheme = _storage_scheme()
    base = f"{scheme}://{environment.STORAGE_ENDPOINT}/"
    object_url = urljoin(base, f"{bucket}/{object_name}")

    return object_url
