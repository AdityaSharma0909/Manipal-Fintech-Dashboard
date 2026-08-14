from __future__ import annotations

from typing import Any, Optional

from django.utils import timezone

from onboarding_v2.models import ApplicationV2, SaasRequestLog


def log_saas_request(
    *,
    application: Optional[ApplicationV2],
    request_type: str,
    payload: Optional[dict[str, Any]] = None,
    response_status: Optional[int] = None,
    response_body: Optional[Any] = None,
    error: Optional[str] = None,
    increment_attempt: bool = False,
) -> SaasRequestLog:
    """
    Upsert a single SAAS log row per application + request type.
    Set increment_attempt=True when initiating a request; call again to store response/error.
    """
    now = timezone.now()
    app_id = application.application_id if application else ""
    log, _ = SaasRequestLog.objects.update_or_create(
        application_identifier=app_id,
        request_type=request_type,
        defaults={
            "application": application,
        },
    )

    if increment_attempt:
        log.attempts += 1
        if not log.first_attempt_at:
            log.first_attempt_at = now
        log.last_attempt_at = now

    if payload is not None:
        log.last_payload = payload
    if response_status is not None:
        log.last_response_status = response_status
    if response_body is not None:
        log.last_response_body = response_body
    # If error explicitly provided, store it; if success status provided, clear last_error.
    if error is not None:
        log.last_error = str(error)
    elif response_status is not None:
        log.last_error = None

    log.save(update_fields=[
        "application",
        "attempts",
        "last_payload",
        "last_response_status",
        "last_response_body",
        "last_error",
        "first_attempt_at",
        "last_attempt_at",
        "modified_at",
    ])
    return log
