from typing import Optional, Union
from django.utils import timezone
from onboarding_v2.constants import ApplicationStage, ApplicationStatus
from onboarding_v2.services import (
    resolve_post_screen_completion,
    resolve_pre_screen_completion,
    sync_lead_status,
)


def log_status_change(application, to_status: str, from_status: Optional[str] = None, user=None, remarks: Optional[str] = None):
    from onboarding_v2.models import ApplicationStatusHistory

    if from_status is None and hasattr(application, "status"):
        from_status = application.status

    return ApplicationStatusHistory.objects.create(
        application=application,
        from_status=from_status,
        to_status=to_status,
        changed_by=user if getattr(user, "is_authenticated", False) else None,
        remarks=remarks,
    )


def save_stage_snapshot(application, stage: str, payload: Union[dict, list], is_complete: bool, user=None):
    from onboarding_v2 import views as views_module

    existing_snapshot = views_module.ApplicationStageSnapshot.objects.filter(
        application=application, stage=stage
    ).first()

    defaults = {"payload": payload, "is_complete": is_complete}
    if is_complete:
        if existing_snapshot and existing_snapshot.completed_at:
            defaults["completed_at"] = existing_snapshot.completed_at
        else:
            defaults["completed_at"] = timezone.now()
    else:
        defaults["completed_at"] = None

    snapshot, _ = views_module.ApplicationStageSnapshot.objects.update_or_create(
        application=application,
        stage=stage,
        defaults=defaults,
    )

    return snapshot



def update_application_progress(application, stage: str, is_complete: bool, payload: Union[dict, list], user=None) -> None:

    if not is_complete:
        return

    if user and getattr(user, "is_authenticated", False):
        application._status_changed_by = user

    application.stage = stage
    update_fields = ["stage", "pre_screen_completion", "post_screen_completion", "stage_payload", "status", "modified_at"]

    if stage in [ApplicationStage.PAN, ApplicationStage.LENDING_PARTNER_BANK, ApplicationStage.LOAN_RANGE_SELECTION, ApplicationStage.PRODUCT_SELECTION, ApplicationStage.BASIC, ApplicationStage.ADDRESS, ApplicationStage.SUBMITTED]:
        pre_pct = resolve_pre_screen_completion(stage)
        if pre_pct is not None:
            application.pre_screen_completion = pre_pct
    else:
        post_pct = resolve_post_screen_completion(stage)
        if post_pct is not None:
            application.post_screen_completion = post_pct

    if stage == ApplicationStage.SUBMITTED:
        application.status = ApplicationStatus.SENT_FOR_PRE_SCREENING
        if not application.submitted_at:
            application.submitted_at = timezone.now()
            update_fields.append("submitted_at")
    elif stage == ApplicationStage.PAN and application.status == ApplicationStatus.DRAFT:
        application.status = ApplicationStatus.IN_PROGRESS
    elif stage == ApplicationStage.SELFIE:
        # After Selfie is submitted, status becomes RH Approval Pending
        application.status = ApplicationStatus.RH_APPROVAL_PENDING
    
    # Defensive update to stage_payload to avoid overwriting dict with list/null
    # Special handling for stages that manage their own complex payload (like list-based FUND_REFUND)
    if stage == ApplicationStage.FUND_REFUND:
        # persist_fund_refund already updated the list in stage_payload
        pass
    elif isinstance(application.stage_payload, dict) and isinstance(payload, dict):
        application.stage_payload = {**application.stage_payload, stage.lower(): payload}
    else:
        application.stage_payload = payload
        
    application.save(
        update_fields=update_fields
    )
    if stage == ApplicationStage.SUBMITTED:
        sync_lead_status(application, ApplicationStatus.SENT_FOR_PRE_SCREENING)
    elif stage == ApplicationStage.PAN and application.status == ApplicationStatus.IN_PROGRESS:
        sync_lead_status(application, ApplicationStatus.IN_PROGRESS)
    elif stage == ApplicationStage.SELFIE and application.status == ApplicationStatus.RH_APPROVAL_PENDING:
        sync_lead_status(application, ApplicationStatus.RH_APPROVAL_PENDING)

