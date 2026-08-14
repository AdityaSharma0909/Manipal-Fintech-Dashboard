from __future__ import annotations

from onboarding_v2.saas import _resolve_jewellery_code_and_name
from onboarding_v2.storage import (
    generate_jewellery_presigned_upload,
    generate_presigned_get,
    generate_presigned_upload,
)
from onboarding_v2.helpers.view_helpers import resolve_jewellery_item_index


def build_jewellery_presign(application, payload: dict) -> dict:
    jewellery_type = payload.get("type_of_jewellery")
    side = str(payload.get("side") or "").upper()
    index = payload.get("index")
    filename = payload.get("filename") or ""
    content_type = payload.get("content_type")

    if side not in ["FRONT", "BACK", "WEIGHING", "CERTIFICATE"]:
        raise ValueError("Invalid side; use FRONT, BACK, WEIGHING, or CERTIFICATE")

    code, _ = _resolve_jewellery_code_and_name(jewellery_type)
    if not code:
        raise ValueError("Invalid jewellery type")

    try:
        idx = int(index)
    except Exception:
        idx = None

    if idx is None:
        idx = resolve_jewellery_item_index(application, jewellery_type)

    return generate_jewellery_presigned_upload(
        application_id=application.application_id,
        code=code,
        side=side,
        index=idx,
        filename=filename,
        content_type=content_type,
    )


def build_document_presign(application, data: dict) -> dict:
    return generate_presigned_upload(
        application_id=application.application_id,
        document_type=data["document_type"],
        filename=data.get("filename"),
        content_type=data.get("content_type"),
        subtype=data.get("subtype"),
    )


def build_document_download_presign(application, data: dict) -> dict:
    file_url = data.get("file_url")
    object_name = data.get("object_name")

    # If document_type provided, try to resolve from ApplicationDocument
    doc_type = data.get("document_type")
    subtype = data.get("subtype")
    if doc_type and not file_url and not object_name:
        doc_qs = application.documents.filter(document_type=doc_type)
        if subtype:
            doc_qs = doc_qs.filter(subtype=subtype)
        doc = doc_qs.order_by("-modified_at").first()
        if not doc:
            raise ValueError("Document not found for given type")
        file_url = doc.file_url
        if not file_url and doc.file:
            file_url = doc.file.url

    try:
        return generate_presigned_get(file_url=file_url, object_name=object_name)
    except Exception as exc:
        raise ValueError(str(exc))
