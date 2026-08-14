import logging
from datetime import timedelta
from typing import Optional

import requests

from celery import shared_task
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from onboarding_v2.constants import ApplicationStatus, LeadStatus, LeadType, ProductSubCategory, TransactionStatus
from onboarding_v2.models import (
    ApplicationV2,
    LeadAutoClosureSetting,
    LeadV2,
    WebhookEvent,
)
from onboarding_v2.notifications import notify_saas_alert
from onboarding_v2.saas import SaasClient, generate_saas_request_id
from onboarding_v2.bureau import run_bureau_check, BureauError
from onboarding_v2.helpers.import_utils import import_pincodes, import_bank_branches
from onboarding_v2.services import sync_lead_status

logger = logging.getLogger(__name__)


@shared_task
def auto_close_leads_task():
    """
    Periodic task to auto-close leads based on LeadAutoClosureSetting.
    """
    try:
        settings = LeadAutoClosureSetting.objects.filter(is_active=True)
        total_closed = 0

        for setting in settings:
            if setting.auto_closure_days is None or setting.auto_closure_days < 1 or setting.auto_closure_days > 3650:
                logger.error(
                    "Skipping invalid auto-closure setting %s for %s - %s with auto_closure_days=%s",
                    setting.id,
                    setting.lead_type,
                    setting.product_subcategory,
                    setting.auto_closure_days,
                )
                continue

            cutoff_date = timezone.now() - timedelta(days=setting.auto_closure_days)

            leads_to_close = LeadV2.objects.filter(
                lead_type=setting.lead_type,
                product_subcategory=setting.product_subcategory,
                status=LeadStatus.ACTIVE,
                created_at__lte=cutoff_date,
            ).exclude(applications__isnull=False)

            count = leads_to_close.count()
            if count > 0:
                logger.info(
                    "Auto-closing %d leads for %s - %s",
                    count,
                    setting.lead_type,
                    setting.product_subcategory,
                )

                for lead in leads_to_close:
                    lead.status = LeadStatus.AUTO_CLOSED
                    lead.save(update_fields=["status", "modified_at"])

                    # Trigger SMS to lead creator
                    creator_phone = getattr(lead.created_by, "phone", None) if lead.created_by else None
                    if creator_phone:
                        try:
                            from utils.sms import SMSService

                            sms_service = SMSService()
                            sms_service.sendLeadAutoClosedNotification(
                                str(creator_phone),
                                lead.customer_name,
                                lead.lead_code,
                            )
                        except Exception as sms_err:
                            logger.error(
                                "Failed to send auto-close SMS for lead %s: %s",
                                lead.id,
                                sms_err,
                            )
                    else:
                        logger.warning(
                            "Skipping auto-close SMS for lead %s because creator phone is missing",
                            lead.id,
                        )
                total_closed += count

        return f"Successfully auto-closed {total_closed} leads"
    except Exception as exc:
        logger.exception("Auto-close leads task failed")
        raise


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def submit_pre_screen_task(self, application_id: str, payload: dict):
    event = None
    application = ApplicationV2.objects.filter(application_id=application_id).first()
    if application:
        application.saas_attempts = (application.saas_attempts or 0) + 1
        application.saas_last_attempt_at = timezone.now()
        application.save(update_fields=["saas_attempts", "saas_last_attempt_at", "modified_at"])
    try:
        logger.info("Task submit_pre_screen start | app=%s payload=%s", application_id, payload)
        client = SaasClient()
        response = client.submit_pre_screen(payload, application=application)
        if application:
            if not application.saas_request_id:
                application.saas_request_id = generate_saas_request_id()
            # status will be finalized by webhook, but capture what SAAS returned
            if isinstance(response, dict) and response.get("status"):
                application.saas_status = response.get("status")
            if isinstance(response, dict):
                application.saas_prescreen_raw = response
                response_data = response.get("data")
                lead_id = response.get("leadId") or (
                    response_data.get("leadId")
                    if isinstance(response_data, dict)
                    else None
                )
                if lead_id:
                    application.saas_lead_id = str(lead_id)
            application.save(
                update_fields=[
                    "saas_status",
                    "saas_lead_id",
                    "saas_request_id",
                    "saas_prescreen_raw",
                    "modified_at",
                ]
            )
        if isinstance(response, dict) and str(response.get("status")).upper() not in ["", "SUCCESS", "ELIGIBLE", "OK"]:
            if application:
                application.status = ApplicationStatus.FAILED_TO_SUBMIT_PRESCREEN
                application.save(update_fields=["status", "modified_at"])
                sync_lead_status(
                    application,
                    ApplicationStatus.FAILED_TO_SUBMIT_PRESCREEN,
                )
            notify_saas_alert(
                "SAAS pre-screen returned non-success",
                {
                    "application_id": application_id,
                    "event_id": event.id if event else None,
                    "status": response.get("status"),
                    "response": response,
                    "payload": payload,
                },
            )
        logger.info("Task submit_pre_screen done | app=%s", application_id)
        return response
    except Exception as exc:
        reason = str(exc)
        status_code = None
        if isinstance(exc, requests.HTTPError) and getattr(exc, "response", None) is not None:
            status_code = exc.response.status_code
            reason = f"{exc} body={exc.response.text}"
        logger.exception("Pre-screen submit failed for %s", application_id)
        notify_saas_alert(
            "SAAS pre-screen failed",
            {
                "application_id": application_id,
                "event_id": event.id if event else None,
                "error": reason,
                "payload": payload,
                "response": getattr(getattr(exc, "response", None), "text", None),
                "attempts": self.request.retries + 1,
            },
        )
        if status_code is not None and 400 <= status_code < 500:
            if application:
                application.status = ApplicationStatus.FAILED_TO_SUBMIT_PRESCREEN
                application.save(update_fields=["status", "modified_at"])
                sync_lead_status(application, ApplicationStatus.FAILED_TO_SUBMIT_PRESCREEN)
            logger.warning("Pre-screen submit non-retriable | app=%s status=%s", application_id, status_code)
            return {"status": "FAILED", "error": reason, "http_status": status_code}
        countdown = min(60 * (2 ** self.request.retries), 600)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def submit_fund_refund_task(self, application_id: str, payload: dict):
    application = ApplicationV2.objects.filter(application_id=application_id).first()
    try:
        logger.info("Task submit_fund_refund start | app=%s payload=%s", application_id, payload)
        client = SaasClient()
        response = client.submit_fund_refund(payload, application=application)
        logger.info("Task submit_fund_refund done from saas tach ---->>>| app=%s response=%s", application_id, response)
        return response
    except Exception as exc:
        reason = str(exc)
        status_code = None
        if isinstance(exc, requests.HTTPError) and getattr(exc, "response", None) is not None:
            status_code = exc.response.status_code
            reason = f"{exc} body={exc.response.text}"
        logger.exception("Fund refund submit failed for %s", application_id)
        notify_saas_alert(
            "SAAS fund refund failed",
            {
                "application_id": application_id,
                "error": reason,
                "payload": payload,
                "attempts": self.request.retries + 1,
            },
        )
        if status_code is not None and 400 <= status_code < 500:
            logger.warning("Fund refund submit non-retriable | app=%s status=%s", application_id, status_code)
            return {"status": "FAILED", "error": reason, "http_status": status_code}
        countdown = min(60 * (2 ** self.request.retries), 600)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def create_loan_task(self, application_id: str, payload: dict):
    event = None
    application = ApplicationV2.objects.filter(application_id=application_id).first()
    if application:
        application.saas_attempts = (application.saas_attempts or 0) + 1
        application.saas_last_attempt_at = timezone.now()
        application.save(update_fields=["saas_attempts", "saas_last_attempt_at", "modified_at"])
    try:
        logger.info("Task create_loan start | app=%s payload=%s", application_id, payload)
        client = SaasClient()
        response = client.create_loan(payload, application=application)
        if application:
            if isinstance(response, dict):
                application.saas_create_loan_status = response.get("status") or application.saas_create_loan_status
                application.saas_create_loan_raw = response
            application.status = ApplicationStatus.SUBMITTED
            application.save(
                update_fields=[
                    "saas_create_loan_status",
                    "saas_create_loan_raw",
                    "status",
                    "modified_at",
                ]
            )
            sync_lead_status(application, ApplicationStatus.SUBMITTED)
        if isinstance(response, dict) and str(response.get("status")).upper() not in ["", "SUCCESS", "ELIGIBLE", "OK"]:
            notify_saas_alert(
                "SAAS create-loan returned non-success",
                {
                    "application_id": application_id,
                    "event_id": event.id if event else None,
                    "status": response.get("status"),
                    "response": response,
                    "payload": payload,
                },
            )
        logger.info("Task create_loan done | app=%s", application_id)
        return response
    except Exception as exc:
        reason = str(exc)
        status_code = None
        if isinstance(exc, requests.HTTPError) and getattr(exc, "response", None) is not None:
            status_code = exc.response.status_code
            reason = f"{exc} body={exc.response.text}"
            if application:
                application.status = ApplicationStatus.FAILED_TO_SUBMIT_CREATE_LOAN
                application.save(update_fields=["status", "modified_at"])
                sync_lead_status(application, ApplicationStatus.FAILED_TO_SUBMIT_CREATE_LOAN)
        logger.exception("Create-loan failed for %s", application_id)
        notify_saas_alert(
            "SAAS create-loan failed",
            {
                "application_id": application_id,
                "event_id": event.id if event else None,
                "error": reason,
                "payload": payload,
                "attempts": self.request.retries + 1,
            },
        )
        if status_code is not None and 400 <= status_code < 500:
            logger.warning("Create-loan non-retriable | app=%s status=%s", application_id, status_code)
            return {"status": "FAILED", "error": reason, "http_status": status_code}
        countdown = min(60 * (2 ** self.request.retries), 600)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(bind=True, max_retries=0)
def save_onboard_details_task(self, application_id: str, payload: dict):
    application = ApplicationV2.objects.filter(application_id=application_id).first()
    if application:
        application.saas_attempts = (application.saas_attempts or 0) + 1
        application.saas_last_attempt_at = timezone.now()
        application.save(update_fields=["saas_attempts", "saas_last_attempt_at", "modified_at"])
    try:
        logger.info("Task save_onboard_details start | app=%s payload=%s", application_id, payload)
        client = SaasClient()
        response = client.save_onboard_details(payload, application=application)
        if application:
            if isinstance(response, dict):
                application.saas_status = response.get("status") or application.saas_status
                application.saas_create_loan_raw = response

                message = response.get("message") or ""
                if "Onboard data already exist" in message:
                    logger.warning("Application already exists | app=%s msg=%s", application_id, message)
                    application.save(
                        update_fields=[
                            "saas_status",
                            "saas_create_loan_raw",
                            "modified_at",
                        ]
                    )
                    return response

            application.status = ApplicationStatus.SUBMITTED_TO_UNDERWRITING
            application.save(
                update_fields=[
                    "saas_status",
                    "saas_create_loan_raw",
                    "status",
                    "modified_at",
                ]
            )
            sync_lead_status(application, ApplicationStatus.SUBMITTED_TO_UNDERWRITING)
        logger.info("Task save_onboard_details done | app=%s", application_id)
        return response
    except Exception as exc:
        reason = str(exc)
        status_code = None
        if isinstance(exc, requests.HTTPError) and getattr(exc, "response", None) is not None:
            status_code = exc.response.status_code
            reason = f"{exc} body={exc.response.text}"
        logger.exception("Save onboard details failed for %s", application_id)
        notify_saas_alert(
            "SAAS save onboard details failed",
            {
                "application_id": application_id,
                "error": reason,
                "payload": payload,
            },
        )
        if application:
            application.status = ApplicationStatus.FAILED_TO_SUBMIT_TO_UNDERWRITING
            application.save(update_fields=["status", "modified_at"])
            sync_lead_status(application, ApplicationStatus.FAILED_TO_SUBMIT_TO_UNDERWRITING)
        logger.warning("Save onboard details failed | app=%s status=%s", application_id, status_code)
        return {"status": "FAILED", "error": reason, "http_status": status_code}



@shared_task(bind=True, max_retries=0)
def update_onboard_details_task(self, application_id: str, payload: dict):
    application = ApplicationV2.objects.filter(application_id=application_id).first()
    if application:
        application.saas_attempts = (application.saas_attempts or 0) + 1
        application.saas_last_attempt_at = timezone.now()
        application.save(update_fields=["saas_attempts", "saas_last_attempt_at", "modified_at"])
    try:
        logger.info("Task update_onboard_details start | app=%s payload=%s", application_id, payload)
        client = SaasClient()
        response = client.update_onboard_details(payload, application=application)
        if application:
            if isinstance(response, dict):
                application.saas_status = response.get("status") or application.saas_status
                application.saas_create_loan_raw = response

                message = response.get("message") or ""
                if "Onboard data already exist" in message:
                    logger.warning("Application already exists in SAAS (update) | app=%s msg=%s", application_id, message)
                    application.save(
                        update_fields=[
                            "saas_status",
                            "saas_create_loan_raw",
                            "modified_at",
                        ]
                    )
                    return response

            application.status = ApplicationStatus.SUBMITTED_TO_UNDERWRITING
            application.save(
                update_fields=[
                    "saas_status",
                    "saas_create_loan_raw",
                    "status",
                    "modified_at",
                ]
            )
            sync_lead_status(application, ApplicationStatus.SUBMITTED_TO_UNDERWRITING)
        logger.info("Task update_onboard_details done | app=%s", application_id)
        return response
    except Exception as exc:
        reason = str(exc)
        status_code = None
        if isinstance(exc, requests.HTTPError) and getattr(exc, "response", None) is not None:
            status_code = exc.response.status_code
            reason = f"{exc} body={exc.response.text}"
        logger.exception("Update onboard details failed for %s", application_id)
        notify_saas_alert(
            "SAAS update onboard details failed",
            {
                "application_id": application_id,
                "error": reason,
                "payload": payload,
            },
        )
        if application:
            application.status = ApplicationStatus.FAILED_TO_SUBMIT_TO_UNDERWRITING
            application.save(update_fields=["status", "modified_at"])
            sync_lead_status(application, ApplicationStatus.FAILED_TO_SUBMIT_TO_UNDERWRITING)
        logger.warning("Update onboard details failed | app=%s status=%s", application_id, status_code)
        return {"status": "FAILED", "error": reason, "http_status": status_code}


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def upload_doc_task(self, application_id: str, payload: dict):
    try:
        logger.info("Task upload_doc start | app=%s", application_id)
        client = SaasClient()
        response = client.upload_document(payload)
        logger.info("Task upload_doc done | app=%s", application_id)
        return response
    except Exception as exc:
        reason = str(exc)
        if isinstance(exc, requests.HTTPError) and getattr(exc, "response", None) is not None:
            reason = f"{exc} body={exc.response.text}"
        logger.exception("Doc upload failed for %s", application_id)
        notify_saas_alert(
            "SAAS doc upload failed",
            {
                "application_id": application_id,
                "error": reason,
                "payload": payload,
                "attempts": self.request.retries + 1,
            },
        )
        countdown = min(60 * (2 ** self.request.retries), 600)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def notify_rh_approval_task(self, application_id: str, payload: dict):
    try:
        logger.info("Task notify_rh_approval start | app=%s payload=%s", application_id, payload)
        client = SaasClient()
        response = client.notify_rh_action(payload)
        logger.info("Task notify_rh_approval done | app=%s response=%s", application_id, response)
        return response
    except Exception as exc:
        logger.exception("RH approval notification failed for %s", application_id)
        # For notification, we might want to retry but maybe with a longer delay or fewer attempts
        # if the external service is down.
        countdown = min(60 * (2 ** self.request.retries), 600)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def run_bureau_check_task(self, application_id: str, event_id: Optional[str] = None):
    event = None
    if event_id:
        event = WebhookEvent.objects.filter(id=event_id).first()

    # If token not configured, skip gracefully (especially in DEV)
    if not getattr(settings, "SIGNZY_EXP_AUTH_TOKEN", None):
        logger.info("Skipping bureau check (SIGNZY_EXP_AUTH_TOKEN missing) | app=%s", application_id)
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
            application.bureau_decision = application.bureau_decision or "PENDING"
            application.save(update_fields=["bureau_decision", "modified_at"])
        except ApplicationV2.DoesNotExist:
            pass
        if event:
            event.status = WebhookEvent.Status.PROCESSED
            event.last_error = None
            event.retry_count = 0
            event.next_retry_at = None
            event.save(update_fields=["status", "last_error", "retry_count", "next_retry_at", "modified_at"])
        return {"status": "skipped"}

    try:
        application = ApplicationV2.objects.get(application_id=application_id)
    except ApplicationV2.DoesNotExist:
        logger.error("Application %s not found for bureau check", application_id)
        if event:
            event.status = WebhookEvent.Status.FAILED
            event.last_error = "Application not found"
            event.retry_count += 1
            event.next_retry_at = timezone.now() + timedelta(minutes=5)
            event.save(update_fields=["status", "last_error", "retry_count", "next_retry_at", "modified_at"])
        notify_saas_alert(
            "Bureau check failed (app missing)",
            {"application_id": application_id, "event_id": event_id},
        )
        return {"status": "not_found"}
    try:
        result = run_bureau_check(application)
        decision = result.get("decision")
        score = result.get("score")
        raw = result.get("raw") or {}
        bureau_pull_date = timezone.now().date()
        bureau_name = application.bureau_name or getattr(settings, "SIGNZY_BUREAU_NAME", "") or "cibil"
        consent_ip = application.consent_ip or getattr(settings, "SIGNZY_CONSENT_IP", "") or None
        consent_ts = application.consent_timestamp
        if not consent_ts:
            consent_ts = timezone.now()
        ref_number = None
        report_link = None
        try:
            ref_number = (
                raw.get("data", {})
                .get("jsonExperianReport", {})
                .get("ENQUIRY_DETAILS", {})
                .get("ENQUIRY_NUMBER")
            )
        except Exception:
            ref_number = None
        try:
            report_link = raw.get("data", {}).get("pdfExperianReport")
        except Exception:
            report_link = None
        application.bureau_score = score
        if decision:
            application.bureau_decision = decision
        application.bureau_raw = raw
        application.bureau_pull_date = bureau_pull_date
        application.bureau_name = bureau_name
        if consent_ip:
            application.consent_ip = consent_ip
        if consent_ts:
            application.consent_timestamp = consent_ts
        if ref_number:
            application.bureau_reference_number = ref_number
        if report_link:
            application.bureau_report_link = report_link
        # Eligibility is represented by the bureau decision and ELIGIBILITY stage.
        # Only a failed bureau decision changes the application workflow status.
        status_changed = False
        if score is not None and score < 500:
            application.status = ApplicationStatus.NOT_ELIGIBLE
            status_changed = True
        elif decision == "DECLINED":
            application.status = ApplicationStatus.NOT_ELIGIBLE
            status_changed = True
        elif application.loan_type == LeadType.CO_LENDING:
            application.status = ApplicationStatus.ELIGIBLE
            status_changed = True
        update_fields = [
            "bureau_score",
            "bureau_decision",
            "bureau_raw",
            "bureau_pull_date",
            "bureau_name",
            "modified_at",
        ]
        if status_changed:
            update_fields.append("status")
        if ref_number:
            update_fields.append("bureau_reference_number")
        if report_link:
            update_fields.append("bureau_report_link")
        if consent_ip:
            update_fields.append("consent_ip")
        if consent_ts:
            update_fields.append("consent_timestamp")
        application.save(update_fields=update_fields)
        if status_changed:
            sync_lead_status(application, application.status)
        logger.info("Task bureau_check done | app=%s decision=%s score=%s", application_id, decision, score)
        if event:
            event.status = WebhookEvent.Status.PROCESSED
            event.last_error = None
            event.retry_count = 0
            event.next_retry_at = None
            event.save(update_fields=["status", "last_error", "retry_count", "next_retry_at", "modified_at"])
        return result
    except Exception as exc:
        logger.exception("Bureau check failed for %s", application_id)
        if event:
            event.status = WebhookEvent.Status.FAILED
            event.last_error = str(exc)
            event.retry_count += 1
            event.next_retry_at = timezone.now() + timedelta(minutes=10)
            event.save(update_fields=["status", "last_error", "retry_count", "next_retry_at", "modified_at"])
        notify_saas_alert(
            "Bureau check failed",
            {
                "application_id": application_id,
                "event_id": event_id,
                "error": str(exc),
                "attempts": self.request.retries + 1,
            },
        )
        countdown = min(60 * (2 ** self.request.retries), 600)
        raise self.retry(exc=exc, countdown=countdown)


@shared_task(bind=True)
def retry_failed_webhook_events(self, max_retries: int = 5):
    """
    Sweep DB for failed/received events that need re-enqueue.
    """
    now = timezone.now()
    qs = WebhookEvent.objects.filter(
        status__in=[WebhookEvent.Status.RECEIVED, WebhookEvent.Status.FAILED],
    ).filter(models.Q(next_retry_at__lte=now) | models.Q(next_retry_at__isnull=True))

    count = 0
    for event in qs[:200]:
        if event.retry_count >= max_retries:
            continue
        event.status = WebhookEvent.Status.QUEUED
        event.next_retry_at = None
        event.save(update_fields=["status", "next_retry_at", "modified_at"])
        run_bureau_check_task.delay(event.application_id, str(event.id))
        count += 1
    logger.info("retry_failed_webhook_events enqueued=%s", count)
    return {"enqueued": count}


@shared_task(bind=True)
def import_pincodes_task(self, stored_path: str, truncate: bool = False):
    """
    Async import pincodes from a stored file path (default storage). Deletes the file after import.
    """
    try:
        logger.info("Import pincodes task start | path=%s truncate=%s", stored_path, truncate)
        with default_storage.open(stored_path, "rb") as fh:
            count = import_pincodes(fh, truncate=truncate)
    finally:
        try:
            default_storage.delete(stored_path)
        except Exception:
            logger.warning("Failed to delete temp pincode file %s", stored_path)
    logger.info("Import pincodes task done | path=%s imported=%s", stored_path, count)
    return {"imported": count}


@shared_task(bind=True)
def import_bank_branches_task(self, stored_path: str, truncate: bool = False, lender_code: str = None, bank_name: str = None):
    """
    Async import bank branches from a stored file path (default storage). Deletes the file after import.
    """
    try:
        logger.info(
            "Import bank branches task start | path=%s truncate=%s lender_code=%s bank_name=%s",
            stored_path,
            truncate,
            lender_code,
            bank_name,
        )
        with default_storage.open(stored_path, "rb") as fh:
            count = import_bank_branches(fh, truncate=truncate, lender_code=lender_code, bank_name=bank_name)
    finally:
        try:
            default_storage.delete(stored_path)
        except Exception:
            logger.warning("Failed to delete temp branch file %s", stored_path)
    logger.info("Import bank branches task done | path=%s imported=%s", stored_path, count)
    return {"imported": count}


@shared_task(name='onboarding_v2.tasks.export_banca_leads_hourly_task')
def export_banca_leads_hourly_task(recipient_email=None):
    """
    Periodic hourly task that exports all historical leads of the BANCA team to an Excel file and emails it.
    """
    import logging
    import traceback
    from django.utils import timezone
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from utils.envSetup import environment
    from onboarding_v2.models import LeadV2
    from onboarding_v2.helpers.lead_export_helpers import generate_leads_excel

    logger = logging.getLogger(__name__)
    logger.info("Hourly Non-GL leads export task started.")

    try:
        # Filter for all leads that are non-gold loan (exclude GOLD_LOAN subcategory)
        qs = LeadV2.objects.exclude(product_subcategory=ProductSubCategory.GOLD_LOAN).prefetch_related("applications")
        total_count = qs.count()

        if total_count == 0:
            logger.info("No Non-GL leads found to export.")
            return "No Non-GL leads found to export."

        # Generate the Excel content using the shared helper
        excel_file = generate_leads_excel(qs)
        if not excel_file:
            logger.info("Failed to generate Excel sheet or no rows returned.")
            return "Failed to generate Excel sheet or no rows returned."

        excel_content = excel_file.getvalue()

        # Send Email
        now_local = timezone.localtime(timezone.now())
        report_date_str = now_local.strftime("%d %b, %Y, %I:%M %p")

        context = {
            'report_date': report_date_str,
            'total_count': total_count,
        }

        html_content = render_to_string('onboarding_v2/email/banca_leads_report.html', context)
        text_content = f"Non-GL Lead Report ({report_date_str})\n\nTotal Leads: {total_count}"

        raw_recipients = recipient_email or getattr(environment, 'BANCA_LEADS_EXPORT_EMAIL', None) or environment.DEFAULT_TO_EMAIL
        if not raw_recipients:
            logger.error("Recipient email not configured.")
            return "Recipient email not configured."

        # Parse recipients list
        if isinstance(raw_recipients, str):
            recipient_list = [e.strip() for e in raw_recipients.split(",") if e.strip()]
        else:
            recipient_list = raw_recipients if isinstance(raw_recipients, list) else [raw_recipients]

        # Parse CC list
        cc_list = None
        raw_cc = getattr(environment, 'BANCA_LEADS_EXPORT_CC', None)
        if raw_cc:
            if isinstance(raw_cc, str):
                cc_list = [e.strip() for e in raw_cc.split(",") if e.strip()]
            else:
                cc_list = raw_cc if isinstance(raw_cc, list) else [raw_cc]

        subject = "Non-GL Lead Report"
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            cc=cc_list,
        )
        email.attach_alternative(html_content, "text/html")
        email.attach(
            f"non_gl_leads_report_{now_local.strftime('%Y%m%d_%H%M%S')}.xlsx",
            excel_content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        email.send()

        logger.info("Non-GL Lead Report successfully sent to %s (CC: %s)", ", ".join(recipient_list), ", ".join(cc_list) if cc_list else "None")
        return f"Report containing {total_count} leads successfully sent to {', '.join(recipient_list)}"

    except Exception as e:
        logger.exception("Failed executing hourly Non-GL leads export task")
        return f"Error: {str(e)}"


@shared_task(name='onboarding_v2.tasks.export_multi_table_report_task')
def export_multi_table_report_task(recipient_email=None):
    """
    Periodic task that exports the GL Punching multi-table report and emails it.
    """
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives
    from django.utils import timezone
    from utils.envSetup import environment
    from onboarding_v2.models import ApplicationV2
    from onboarding_v2.views.export_multi_table import build_multi_table_export_workbook

    logger.info("Multi-table export report task started.")

    try:
        qs = ApplicationV2.objects.all().order_by("-created_at")
        excel_file, total_count = build_multi_table_export_workbook(qs)
        excel_content = excel_file.getvalue()

        now_local = timezone.localtime(timezone.now())
        report_date_str = now_local.strftime("%d %b, %Y, %I:%M %p")

        raw_recipients = (
            recipient_email
            or getattr(environment, 'MULTI_TABLE_EXPORT_EMAIL', None)
            or environment.DEFAULT_TO_EMAIL
        )
        if not raw_recipients:
            logger.error("Multi-table export recipient email not configured.")
            return "Recipient email not configured."

        if isinstance(raw_recipients, str):
            recipient_list = [e.strip() for e in raw_recipients.split(",") if e.strip()]
        else:
            recipient_list = raw_recipients if isinstance(raw_recipients, list) else [raw_recipients]

        raw_cc = getattr(environment, 'MULTI_TABLE_EXPORT_CC', None)
        cc_list = None
        if raw_cc:
            if isinstance(raw_cc, str):
                cc_list = [e.strip() for e in raw_cc.split(",") if e.strip()]
            else:
                cc_list = raw_cc if isinstance(raw_cc, list) else [raw_cc]

        subject = "GL Punching Report"
        text_content = (
            f"GL Punching Report ({report_date_str})\n\n"
            f"Total Applications: {total_count}"
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            cc=cc_list,
        )
        email.attach(
            f"gl_punching_report_{now_local.strftime('%Y%m%d_%H%M%S')}.xlsx",
            excel_content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        email.send()

        logger.info(
            "Multi-table export report sent to %s (CC: %s)",
            ", ".join(recipient_list),
            ", ".join(cc_list) if cc_list else "None",
        )
        return f"Report containing {total_count} applications sent to {', '.join(recipient_list)}"
    except Exception as e:
        logger.exception("Failed executing multi-table export report task")
        return f"Error: {str(e)}"


@shared_task(name='onboarding_v2.tasks.export_bank_crm_report_task')
def export_bank_crm_report_task(recipient_email=None):
    """
    Periodic task that exports today's bank CRM trace report and emails it.
    """
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives
    from django.utils import timezone
    from utils.envSetup import environment
    from onboarding_v2.helpers.bank_crm_report import build_bank_crm_report_workbook
    from onboarding_v2.models import BankLeadTrace

    logger.info("Bank CRM report task started.")

    try:
        now_local = timezone.localtime(timezone.now())
        start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end_local = start_local + timedelta(days=1)

        traces = (
            BankLeadTrace.objects.filter(created_at__gte=start_local, created_at__lt=end_local)
            .select_related("lead", "created_by")
            .order_by("created_at")
        )
        excel_file, total_count = build_bank_crm_report_workbook(traces)

        raw_recipients = (
            recipient_email
            or getattr(environment, 'BANK_CRM_REPORT_EMAIL', None)
            or environment.DEFAULT_TO_EMAIL
        )
        if not raw_recipients:
            logger.error("Bank CRM report recipient email not configured.")
            return "Recipient email not configured."

        if isinstance(raw_recipients, str):
            recipient_list = [email.strip() for email in raw_recipients.split(",") if email.strip()]
        else:
            recipient_list = raw_recipients if isinstance(raw_recipients, list) else [raw_recipients]

        raw_cc = getattr(environment, 'BANK_CRM_REPORT_CC', None)
        cc_list = None
        if raw_cc:
            if isinstance(raw_cc, str):
                cc_list = [email.strip() for email in raw_cc.split(",") if email.strip()]
            else:
                cc_list = raw_cc if isinstance(raw_cc, list) else [raw_cc]

        report_date_str = now_local.strftime("%d %b, %Y")
        subject = f"Bank CRM Report - {report_date_str}"
        body = (
            f"Hi Team,\n\n"
            f"Please find attached the Bank CRM Report for {report_date_str}.\n\n"
            f"Total Records: {total_count}\n\n"
            f"Thanks & Regards"
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            cc=cc_list,
        )
        email.attach(
            "Bank CRM Report.xlsx",
            excel_file.getvalue(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        email.send()

        logger.info(
            "Bank CRM report sent to %s (CC: %s)",
            ", ".join(recipient_list),
            ", ".join(cc_list) if cc_list else "None",
        )
        return f"Bank CRM report containing {total_count} records sent to {', '.join(recipient_list)}"
    except Exception as e:
        logger.exception("Failed executing Bank CRM report task")
        return f"Error: {str(e)}"


@shared_task(name='onboarding_v2.tasks.export_bt_disbursal_report_task')
def export_bt_disbursal_report_task(recipient_email=None):
    """
    Periodic task that exports the BT Disbursal Report and emails it.
    """
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.utils import timezone
    from utils.envSetup import environment
    from onboarding_v2.models import ApplicationV2
    from onboarding_v2.constants import LeadType
    from onboarding_v2.views.export_bt_disbursal import build_bt_disbursal_report_workbook

    logger.info("BT Disbursal Report task started.")

    try:
        qs = (
            ApplicationV2.objects.filter(loan_type=LeadType.BALANCE_TRANSFER)
            .select_related(
                "lead",
                "lead__created_by",
                "punched_by",
                "assigned_rh",
            )
            .prefetch_related("punched_loans", "stage_snapshots")
            .order_by("-created_at")
        )
        excel_file, total_count = build_bt_disbursal_report_workbook(qs)
        excel_content = excel_file.getvalue()

        now_local = timezone.localtime(timezone.now())
        report_date_str = now_local.strftime("%d %b, %Y, %I:%M %p")

        raw_recipients = (
            recipient_email
            or getattr(environment, 'BT_DISBURSAL_EXPORT_EMAIL', None)
            or environment.DEFAULT_TO_EMAIL
        )
        if not raw_recipients:
            logger.error("BT Disbursal Report recipient email not configured.")
            return "Recipient email not configured."

        if isinstance(raw_recipients, str):
            recipient_list = [email.strip() for email in raw_recipients.split(",") if email.strip()]
        else:
            recipient_list = raw_recipients if isinstance(raw_recipients, list) else [raw_recipients]

        raw_cc = getattr(environment, 'BT_DISBURSAL_EXPORT_CC', None)
        cc_list = None
        if raw_cc:
            if isinstance(raw_cc, str):
                cc_list = [email.strip() for email in raw_cc.split(",") if email.strip()]
            else:
                cc_list = raw_cc if isinstance(raw_cc, list) else [raw_cc]

        context = {
            'report_date': report_date_str,
            'total_count': total_count,
        }
        html_content = render_to_string('onboarding_v2/email/bt_disbursal_report.html', context)
        text_content = f"BT Disbursal Report ({report_date_str})\n\nTotal Records: {total_count}"

        subject = "BT Disbursal Report"
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            cc=cc_list,
        )
        email.attach_alternative(html_content, "text/html")
        email.attach(
            f"bt_disbursal_report_{now_local.strftime('%Y%m%d_%H%M%S')}.xlsx",
            excel_content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        email.send()

        logger.info(
            "BT Disbursal Report sent to %s (CC: %s)",
            ", ".join(recipient_list),
            ", ".join(cc_list) if cc_list else "None",
        )
        return f"BT Disbursal Report containing {total_count} records sent to {', '.join(recipient_list)}"
    except Exception as e:
        logger.exception("Failed executing BT Disbursal Report task")
        return f"Error: {str(e)}"


@shared_task(name='onboarding_v2.tasks.export_new_gl_against_bt_report_task')
def export_new_gl_against_bt_report_task(recipient_email=None):
    """
    Periodic task that exports the New GL Against BT Report and emails it.
    """
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.utils import timezone
    from utils.envSetup import environment
    from onboarding_v2.models import ApplicationV2
    from onboarding_v2.constants import LeadType
    from onboarding_v2.views.export_new_gl_against_bt import build_new_gl_against_bt_report_workbook

    logger.info("New GL Against BT Report task started.")

    try:
        qs = (
            ApplicationV2.objects.filter(loan_type=LeadType.BALANCE_TRANSFER)
            .select_related(
                "lead",
                "lead__created_by",
                "punched_by",
                "assigned_rh",
            )
            .prefetch_related("punched_loans", "stage_snapshots")
            .order_by("-created_at")
        )
        excel_file, total_count = build_new_gl_against_bt_report_workbook(qs)
        excel_content = excel_file.getvalue()

        now_local = timezone.localtime(timezone.now())
        report_date_str = now_local.strftime("%d %b, %Y, %I:%M %p")

        raw_recipients = (
            recipient_email
            or getattr(environment, 'NEW_GL_AGAINST_BT_EXPORT_EMAIL', None)
            or environment.DEFAULT_TO_EMAIL
        )
        if not raw_recipients:
            logger.error("New GL Against BT Report recipient email not configured.")
            return "Recipient email not configured."

        if isinstance(raw_recipients, str):
            recipient_list = [email.strip() for email in raw_recipients.split(",") if email.strip()]
        else:
            recipient_list = raw_recipients if isinstance(raw_recipients, list) else [raw_recipients]

        raw_cc = getattr(environment, 'NEW_GL_AGAINST_BT_EXPORT_CC', None)
        cc_list = None
        if raw_cc:
            if isinstance(raw_cc, str):
                cc_list = [email.strip() for email in raw_cc.split(",") if email.strip()]
            else:
                cc_list = raw_cc if isinstance(raw_cc, list) else [raw_cc]

        context = {
            'report_date': report_date_str,
            'total_count': total_count,
        }
        html_content = render_to_string('onboarding_v2/email/new_gl_against_bt_report.html', context)
        text_content = f"New GL Against BT Report ({report_date_str})\n\nTotal Records: {total_count}"

        subject = "New GL Against BT Report"
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            cc=cc_list,
        )
        email.attach_alternative(html_content, "text/html")
        email.attach(
            f"new_gl_against_bt_report_{now_local.strftime('%Y%m%d_%H%M%S')}.xlsx",
            excel_content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        email.send()

        logger.info(
            "New GL Against BT Report sent to %s (CC: %s)",
            ", ".join(recipient_list),
            ", ".join(cc_list) if cc_list else "None",
        )
        return f"New GL Against BT Report containing {total_count} records sent to {', '.join(recipient_list)}"
    except Exception as e:
        logger.exception("Failed executing New GL Against BT Report task")
        return f"Error: {str(e)}"


@shared_task(name='onboarding_v2.tasks.export_tele_centre_report_task')
def export_tele_centre_report_task(recipient_email=None):
    """
    Periodic task that exports the Tele Centre Report and emails it.
    """
    import os
    import datetime
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives
    from django.utils import timezone
    from utils.envSetup import environment
    from onboarding_v2.models import LoanPunchV2
    from onboarding_v2.views.export_tele_centre_report import build_tele_centre_report_workbook

    logger.info("Tele Centre Report task started.")

    try:
        # Determine yesterday's date range
        now_local = timezone.localtime(timezone.now())
        yesterday = now_local.date() - datetime.timedelta(days=1)
        
        start_dt = timezone.make_aware(datetime.datetime.combine(yesterday, datetime.time.min))
        end_dt = timezone.make_aware(datetime.datetime.combine(yesterday, datetime.time.max))

        # Query LoanPunchV2 records punched yesterday
        loan_punches = (
            LoanPunchV2.objects.filter(created_at__range=(start_dt, end_dt))
            .order_by("-created_at")
        )

        excel_file, total_count = build_tele_centre_report_workbook(loan_punches)
        excel_content = excel_file.getvalue()

        report_date_str = yesterday.strftime("%d %b, %Y")

        # Resolve recipients & cc
        raw_recipients = (
            recipient_email
            or os.environ.get("TELE_CENTRE_EXPORT_EMAIL")
            or getattr(environment, 'TELE_CENTRE_EXPORT_EMAIL', None)
            # or "vaishali.bhat@manipalfintech.com, rahul.sinha@manipalfintech.com, md.kalimuzzaman@manipalfintech.com, bhawna.kulegi@manipalfintech.com"
        )
        
        if isinstance(raw_recipients, str):
            recipient_list = [email.strip() for email in raw_recipients.split(",") if email.strip()]
        else:
            recipient_list = raw_recipients if isinstance(raw_recipients, list) else [raw_recipients]

        raw_cc = (
            os.environ.get("TELE_CENTRE_EXPORT_CC")
            or getattr(environment, 'TELE_CENTRE_EXPORT_CC', None)
            # or "puneet.sharma@manipalfintech.com, mukesh.k@manipalfintech.com, Sylvester.domingo@manipalfintech.com, rahul.gupta@manipalfintech.com"
        )
        
        if isinstance(raw_cc, str):
            cc_list = [email.strip() for email in raw_cc.split(",") if email.strip()]
        else:
            cc_list = raw_cc if isinstance(raw_cc, list) else [raw_cc]

        text_content = (
            f"Hi Team,\n\n"
            f"Please find the Tele Centre (Customer Details For Tele) Report attached to this email. "
            f"This report covers loans punched on {report_date_str}.\n\n"
            f"Total Applications: {total_count}\n\n"
            f"Thanks & Regards"
        )

        subject = f"Customer Details For Tele - {report_date_str}"
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL or "noreply@manipalfintech.com",
            to=recipient_list,
            cc=cc_list,
        )
        email.attach(
            f"Customer_Details_For_Tele_{yesterday.strftime('%Y%m%d')}.xlsx",
            excel_content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        email.send()

        logger.info(
            "Tele Centre Report sent to %s (CC: %s)",
            ", ".join(recipient_list),
            ", ".join(cc_list) if cc_list else "None",
        )
        return f"Tele Centre Report containing {total_count} records sent to {', '.join(recipient_list)}"
    except Exception as e:
        logger.exception("Failed executing Tele Centre Report task")
        return f"Error: {str(e)}"

