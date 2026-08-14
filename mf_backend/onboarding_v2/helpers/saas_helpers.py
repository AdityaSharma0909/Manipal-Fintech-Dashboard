from __future__ import annotations

import logging

from onboarding_v2.constants import ApplicationStage, ApplicationStatus, LeadType
from onboarding_v2.saas import (
    build_rh_approval_notification_payload,
    build_create_loan_payload,
    build_pre_screen_payload,
    build_bt_onboard_payload,
    build_fund_refund_payload,
    generate_saas_request_id,
)
from onboarding_v2.services import resolve_pre_screen_completion, sync_lead_status
from onboarding_v2.tasks import (
    create_loan_task,
    submit_pre_screen_task,
    save_onboard_details_task,
    update_onboard_details_task,
    notify_rh_approval_task,
    submit_fund_refund_task,
)


logger = logging.getLogger(__name__)


def enqueue_pre_screen(application):
    logger.info("enqueue_pre_screen start | app=%s loan_type=%s", application.application_id, application.loan_type)
    application.status = ApplicationStatus.SENT_FOR_PRE_SCREENING
    application.stage = ApplicationStage.ADDRESS
    application.pre_screen_completion = resolve_pre_screen_completion(ApplicationStage.ADDRESS)
    application.save(
        update_fields=["status", "stage", "pre_screen_completion", "modified_at"]
    )
    sync_lead_status(application, ApplicationStatus.SENT_FOR_PRE_SCREENING)

    logger.info("Building pre-screen payload for app=%s", application.application_id)
    try:
        saas_payload = build_pre_screen_payload(application)
        logger.info("Successfully built pre-screen payload for app=%s: %s", application.application_id, saas_payload)
    except Exception as e:
        logger.exception("Failed to build pre-screen payload for app=%s", application.application_id)
        raise

    logger.info("Enqueuing submit_pre_screen_task for app=%s", application.application_id)
    submit_pre_screen_task.delay(application.application_id, saas_payload)
    return saas_payload


def enqueue_create_loan(application):
    # if application.loan_type == LeadType.CO_LENDING:
    #     from onboarding_v2.serializers.state import ApplicationStateSerializer
    #     from decimal import Decimal
    #     from uuid import UUID
    #     from datetime import date, datetime

    #     def sanitize_payload(obj):
    #         if isinstance(obj, dict):
    #             return {k: sanitize_payload(v) for k, v in obj.items()}
    #         elif isinstance(obj, list):
    #             return [sanitize_payload(x) for x in obj]
    #         elif isinstance(obj, Decimal):
    #             fval = float(obj)
    #             if fval.is_integer():
    #                 return int(fval)
    #             return fval
    #         elif isinstance(obj, UUID):
    #             return str(obj)
    #         elif isinstance(obj, (datetime, date)):
    #             return obj.isoformat()
    #         return obj

    #     payload = sanitize_payload(ApplicationStateSerializer(application).data)
    # else:
    payload = build_create_loan_payload(application)
    create_loan_task.delay(application.application_id, payload)
    return payload


def enqueue_bt_onboard(application):
    payload = build_bt_onboard_payload(application)
    logger.info("Enqueue BT onboard | app=%s payload=%s", application.application_id, payload)
    # Running synchronously with .apply() so logs and response appear in the Django terminal
    result = save_onboard_details_task.apply(args=[application.application_id, payload])
    logger.info("BT onboard response | app=%s response=%s", application.application_id, result.result)
    return result.result


def enqueue_bt_update(application):
    payload = build_bt_onboard_payload(application)
    logger.info("Enqueue BT update | app=%s payload=%s", application.application_id, payload)
    # Running synchronously with .apply() to maintain consistency with enqueue_bt_onboard
    result = update_onboard_details_task.apply(args=[application.application_id, payload])
    logger.info("BT update response | app=%s response=%s", application.application_id, result.result)
    return result.result


def enqueue_fund_refund(application, refund_entry):
    """
    Deprecated: Use call_fund_refund_sync instead.
    """
    return call_fund_refund_sync(application, refund_entry)


def call_fund_refund_sync(application, refund_entry):
    """
    Call SaaS fund-refund synchronously and raise ValueError on failure.
    """
    import json
    payload = build_fund_refund_payload(application, refund_entry)
    logger.info("Call Fund Refund sync saas tach payload----->>| app=%s payload=%s", application.application_id, payload)
    
    # Running synchronously with .apply()
    result = submit_fund_refund_task.apply(args=[application.application_id, payload])
    
    if result.failed():
        raise ValueError(f"SaaS submission failed: {result.result}")
    
    response = result.result
    if isinstance(response, dict) and response.get("status") == "FAILED":
        error_msg = response.get("error", "Unknown SaaS error")
        # Robustly extract message from "body={...}" if present
        if "body=" in str(error_msg):
            try:
                # Split at body= and take everything after it
                parts = str(error_msg).split("body=", 1)
                if len(parts) > 1:
                    body_str = parts[1].strip()
                    # SaaS sometimes returns a JSON string in the body
                    import json
                    body_json = json.loads(body_str)
                    if isinstance(body_json, dict) and body_json.get("message"):
                        error_msg = body_json["message"]
            except Exception:
                # Fallback to the original error message if parsing fails
                logger.warning("Failed to parse SaaS error body | error=%s", error_msg)
                pass
        raise ValueError(error_msg)
        
    return response


def enqueue_rh_approval_notification(application):
    payload = build_rh_approval_notification_payload(application)
    logger.info("Enqueue RH approval notification | app=%s payload=%s", application.application_id, payload)
    notify_rh_approval_task.delay(application.application_id, payload)
    return payload
