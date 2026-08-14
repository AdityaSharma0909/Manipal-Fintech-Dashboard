import logging

from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.conf import settings

from utils.responseHandler import HttpResponse
from onboarding_v2.constants import ApplicationStatus
from onboarding_v2.models import ApplicationV2, WebhookEvent
from onboarding_v2.helpers.webhook_helpers import (
    resolve_loan_creation_status,
    resolve_prescreen_status,
    resolve_webhook_purpose,
    resolve_webhook_source,
)
from onboarding_v2.services import sync_lead_status


logger = logging.getLogger(__name__)


class PreScreenStatusWebhookView(APIView):
    """
    Endpoint for SAAS Tech to post pre-screen status updates.
    """

    authentication_classes = []
    permission_classes = []
    renderer_classes = [JSONRenderer]

    def post(self, request):
        # Basic shared-secret validation
        expected_token = getattr(settings, "SAAS_WEBHOOK_SECRET", None)
        provided_token = request.headers.get("X-Saas-Token")
        if expected_token and expected_token != provided_token:
            logger.warning("Webhook token mismatch | provided=%s", provided_token)
            from onboarding_v2 import views as views_module

            views_module.notify_saas_alert(
                "SAAS webhook token mismatch",
                {"provided": provided_token, "payload": request.data},
            )
            return HttpResponse.BadRequest("Invalid webhook token")

        payload = request.data
        application_id = payload.get("applicationId") or payload.get("clientLoanId")
        if not application_id:
            return HttpResponse.BadRequest("applicationId is required")

        source = resolve_webhook_source(payload)
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            logger.error("Webhook application missing | app=%s", application_id)
            from onboarding_v2 import views as views_module

            views_module.notify_saas_alert(
                "SAAS webhook application not found",
                {"application_id": application_id, "payload": payload},
            )
            return HttpResponse.BadRequest("Application not found")

        request_id = payload.get("request_id")
        if request_id:
            event, _ = WebhookEvent.objects.update_or_create(
                request_id=request_id,
                application_id=application_id,
                defaults={
                    "payload": payload,
                    "purpose": WebhookEvent.Purpose.UNKNOWN,
                    "status": WebhookEvent.Status.RECEIVED,
                    "last_error": None,
                    "next_retry_at": None,
                },
            )
        else:
            event = WebhookEvent.objects.create(
                application_id=application_id,
                payload=payload,
                purpose=WebhookEvent.Purpose.UNKNOWN,
                status=WebhookEvent.Status.RECEIVED,
            )

        status_val = payload.get("status")
        application.saas_status = status_val
        van_number = payload.get("van_number")
        save_van_number = bool(van_number)
        if save_van_number:
            application.van_number = van_number

        # Derive purpose (pre-screen vs loan creation vs fund refund)
        purpose = resolve_webhook_purpose(source, status_val, payload)

        event.purpose = purpose

        # Map SAAS status to internal status
        remarks = payload.get("remarks")
        if purpose == WebhookEvent.Purpose.PRESCREEN:
            internal_status, should_queue_bureau = resolve_prescreen_status(status_val, remarks)
            if should_queue_bureau:
                # Defer bureau check to Celery
                application.status = ApplicationStatus.READY_FOR_LOAN
                application.saas_prescreen_remarks = remarks
                save_fields = ["saas_status", "status", "saas_prescreen_remarks", "modified_at"]
                if save_van_number:
                    save_fields.append("van_number")
                application.save(update_fields=save_fields)
                sync_lead_status(application, ApplicationStatus.READY_FOR_LOAN)
                event.status = WebhookEvent.Status.QUEUED
                event.save(update_fields=["status", "purpose", "modified_at"])
                logger.info("Webhook eligible | app=%s bureau=queued payload=%s", application_id, payload)
                from onboarding_v2 import views as views_module

                views_module.run_bureau_check_task.delay(application.application_id, str(event.id))
                return HttpResponse.Success({"status": "received", "bureau": "queued"})
            if internal_status:
                application.status = internal_status
            application.saas_prescreen_remarks = remarks or application.saas_prescreen_remarks
            save_fields = ["saas_status", "status", "saas_prescreen_remarks", "modified_at"]
            if save_van_number:
                save_fields.append("van_number")
            application.save(update_fields=save_fields)
            if internal_status:
                sync_lead_status(application, internal_status)
            event.status = WebhookEvent.Status.PROCESSED
            event.save(update_fields=["status", "purpose", "modified_at"])
            logger.info("Webhook status update | app=%s status=%s payload=%s", application_id, status_val, payload)
            return HttpResponse.Success({"status": "received"})

        if purpose == WebhookEvent.Purpose.LOAN_CREATION:
            application.saas_create_loan_status = status_val or application.saas_create_loan_status
            application.saas_loan_remarks = remarks or application.saas_loan_remarks
            application.saas_create_loan_raw = payload
            internal_status = resolve_loan_creation_status(status_val, remarks)
            if internal_status:
                application.status = internal_status
                save_fields = [
                    "saas_status",
                    "saas_create_loan_status",
                    "saas_loan_remarks",
                    "saas_create_loan_raw",
                    "status",
                    "modified_at",
                ]
            else:
                save_fields = [
                    "saas_status",
                    "saas_create_loan_status",
                    "saas_loan_remarks",
                    "saas_create_loan_raw",
                    "modified_at",
                ]
            if save_van_number:
                save_fields.append("van_number")
            application.save(update_fields=save_fields)
            if internal_status:
                sync_lead_status(application, internal_status)
            event.status = WebhookEvent.Status.PROCESSED
            event.save(update_fields=["status", "purpose", "modified_at"])
            logger.info("Webhook loan update | app=%s status=%s payload=%s", application_id, status_val, payload)
            return HttpResponse.Success({"status": "received", "loan": "updated"})

        if purpose == WebhookEvent.Purpose.FUND_REFUND:
            txn_ref = payload.get("transaction_reference_number")
            status_val = payload.get("status")
            remarks = payload.get("remarks")
            
            # Map SaaS status to internal TransactionStatus
            from onboarding_v2.constants import TransactionStatus
            internal_txn_status = TransactionStatus.UNVERIFIED
            if str(status_val).upper() == "VERIFIED":
                internal_txn_status = TransactionStatus.VERIFIED
            elif str(status_val).upper() in ["REJECTED", "FAILED", "DECLINED"]:
                internal_txn_status = TransactionStatus.REJECTED

            stage_payload = application.stage_payload or {}
            if not isinstance(stage_payload, dict):
                stage_payload = {}
            refunds = stage_payload.get("fund_refund") or []
            if not isinstance(refunds, list):
                refunds = []

            # Check snapshot as fallback if empty/missing in stage_payload
            has_snapshot = False
            snapshot = None
            try:
                from onboarding_v2.models import ApplicationStageSnapshot
                from onboarding_v2.constants import ApplicationStage
                snapshot = application.stage_snapshots.filter(stage=ApplicationStage.FUND_REFUND).first()
                if snapshot:
                    has_snapshot = True
            except Exception:
                pass

            if not refunds and has_snapshot and isinstance(snapshot.payload, list):
                refunds = snapshot.payload

            updated = False
            if isinstance(refunds, list):
                for refund in refunds:
                    if refund.get("transaction_reference_number") == txn_ref:
                        refund["status"] = internal_txn_status
                        refund["remarks"] = remarks or refund.get("remarks", "")
                        updated = True
                        break
                
                if updated:
                    # Update stage_payload
                    stage_payload["fund_refund"] = refunds
                    application.stage_payload = stage_payload
                    application.save(update_fields=["stage_payload", "modified_at"])
                    logger.info("Webhook fund refund update | app=%s txn=%s status=%s", application_id, txn_ref, internal_txn_status)
                    from onboarding_v2.helpers.fund_refund_helpers import update_bt_return_completed_status
                    update_bt_return_completed_status(application, previous_status=application.status)
                    
                    # Update snapshot if it exists to keep in sync
                    if has_snapshot and snapshot:
                        snapshot.payload = refunds
                        snapshot.save(update_fields=["payload", "modified_at"])
                        logger.info("Webhook fund refund snapshot updated | app=%s txn=%s", application_id, txn_ref)
                        
                    from onboarding_v2.helpers.fund_refund_helpers import update_bt_return_completed_status
                    update_bt_return_completed_status(application, previous_status=application.status)
                    
            event.status = WebhookEvent.Status.PROCESSED
            event.save(update_fields=["status", "purpose", "modified_at"])
            return HttpResponse.Success({"status": "received", "fund_refund": "updated" if updated else "not_found"})

        # Fallback: mark processed without side effects
        save_fields = ["saas_status", "modified_at"]
        if save_van_number:
            save_fields.append("van_number")
        application.save(update_fields=save_fields)
        event.status = WebhookEvent.Status.PROCESSED
        event.save(update_fields=["status", "purpose", "modified_at"])
        logger.info(
            "Webhook status update (unknown purpose) | app=%s status=%s payload=%s",
            application_id,
            status_val,
            payload,
        )
        return HttpResponse.Success({"status": "received", "purpose": "unknown"})
