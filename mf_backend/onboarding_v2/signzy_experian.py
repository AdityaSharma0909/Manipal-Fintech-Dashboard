import logging
import requests
from django.conf import settings
import time
from typing import Optional
from django.http import JsonResponse
from django.utils import timezone
from onboarding_v2.CreditScoreRange import CreditScoreRange
from onboarding_v2.constants import ApplicationStage, BureauDecision, ApplicationStatus
from onboarding_v2.saas import _get_snapshot_payload, _split_name
from onboarding_v2.models import ApplicationDocument
from onboarding_v2.serializers.credit_score_details import CreditScoreDetails
from onboarding_v2.storage import upload_to_storage, generate_presigned_get
from onboarding_v2.helpers.persistence_helpers import persist_eligibility
from onboarding_v2.helpers.stage_helpers import save_stage_snapshot, update_application_progress

from cibil_score.validators import (
    BureauScoreValidator,
    DPDDaysValidator,
    # DPDAmountValidator,
    SuitFiledValidator,
    WrittenOffValidator, ValidationStatus)

VALIDATORS = [
    BureauScoreValidator(),
    DPDDaysValidator(),
    # DPDAmountValidator(),
    SuitFiledValidator(),
    WrittenOffValidator()]


NO_SCORE = CreditScoreDetails(range="No Score",score_color= "#ADADAD",
                              score_band= "No Score",
                              score_value=None)

logger = logging.getLogger(__name__)

class BureauError(Exception):
    pass

def bureau_error(message):
    raise BureauError(message)


def _split_experian_name(full_name):
    first_name, _, last_name = _split_name(full_name)
    if first_name and not last_name:
        last_name = first_name
    return first_name, last_name


def _is_no_record_found_response(data):
    if not isinstance(data, dict):
        return False

    messages = []
    if data.get("message"):
        messages.append(data.get("message"))

    error = data.get("error")
    if isinstance(error, dict) and error.get("message"):
        messages.append(error.get("message"))

    return any(str(message).strip().lower() == "no record found" for message in messages)


def _mark_no_record_found_approved(application, raw_data):
    application.bureau_score = None
    application.bureau_name = "EXPERIAN"
    application.bureau_pull_date = timezone.now().date()
    application.bureau_raw = raw_data
    application.score_color = NO_SCORE.score_color
    application.bureau_decision = BureauDecision.APPROVED
    application.save(update_fields=[
        "bureau_score", "bureau_name", "bureau_pull_date",
        "bureau_raw", "bureau_decision", "score_color", "modified_at"
    ])

    result = {
        "overall_success": True,
        "message": "No Record Found",
        "results": [],
    }
    eligibility_payload = {
        "credit_bureau_url": None,
        "score_band": NO_SCORE.score_band,
        "score_color": NO_SCORE.score_color,
        "score_value": NO_SCORE.score_value,
        "metadata": {"buearu_check_result": result}
    }
    persist_eligibility(application, eligibility_payload)
    save_stage_snapshot(application, ApplicationStage.ELIGIBILITY, eligibility_payload, True)
    update_application_progress(application, ApplicationStage.ELIGIBILITY, True, eligibility_payload)

    return JsonResponse({
        "status": True,
        "message": "No bureau record found; application approved",
        "data": {
            "score_band": NO_SCORE.score_band,
            "score_color": NO_SCORE.score_color,
            "score_value": NO_SCORE.score_value,
            "credit_buearu_pdf_url": None,
            "credit_buearu_excel_url": None,
            "buearu_check_result": result,
        }
    }, status=200)


def run_experian_bureau_check(application):
    api_url = getattr(settings, "SIGNZY_EXP_API_URL", None) or "https://api-preproduction.signzy.app/api/v3/bureau/experian-bureau-reort"
    auth_token = getattr(settings, "SIGNZY_EXP_AUTH_TOKEN", None)
    if not auth_token:
        return JsonResponse({
            "status": False,
            "message": "SIGNZY_EXP_AUTH_TOKEN not configured",
            "data": None
        }, status=500)

    try:
        payload = build_experian_payload(application)
        print("payload------->>>", payload)
    except (BureauError, ValueError) as exc:
        return JsonResponse({
            "status": False,
            "message": str(exc),
            "data": None
        }, status=400)

    headers = {
        "Content-Type": "application/json",
        "Authorization": auth_token,
    }
    try:      
        resp = requests.post(api_url, json=payload, headers=headers, timeout=30)
        data = resp.json() if resp.text else {}

        if _is_no_record_found_response(data):
            return _mark_no_record_found_approved(application, data)

        if "error" in data:
            return JsonResponse({
                "status": False,
                "message": data["error"]["message"],
            }, status=404)

        if "message" in data and "data" not in data:
            return JsonResponse({
                "status": False,
                "message": data["message"],
            }, status=404)

        # Extract score and report URLs
        score = None
        excel_url = None
        pdf_url = None

        try:
            # Signzy usually nests the report under data.jsonExperianReport
            # But sometimes it might be flat or data might be null on error
            resp_data_payload = data.get("data")
            if isinstance(resp_data_payload, dict):
                report_data = resp_data_payload.get("jsonExperianReport") or resp_data_payload or data
                excel_url = resp_data_payload.get("excelExperianReport")
                pdf_url = resp_data_payload.get("pdfExperianReport")
            else:
                report_data = data

            if isinstance(report_data, dict):
                score_section = report_data.get("SCORE") or report_data.get("Score") or {}
                if isinstance(score_section, dict):
                    score = score_section.get("FCIREXScore") or score_section.get("FCIRExScore")
            
            logger.info(f"Extracted bureau details| score={score} excel_url={excel_url} pdf_url={pdf_url}")
        except Exception as exc:
            logger.error(f"Failed to parse Experian score details: {str(exc)}")

        credit_score_details = get_credit_score_details(score)
        result = run_bureau_check(data)

        # Download and upload bureau report to e2e/storage
        bureau_report_url = None
        if pdf_url:
            try:
                pdf_resp = requests.get(pdf_url, timeout=30)
                if pdf_resp.status_code == 200:
                    bureau_report_url = upload_to_storage(
                        application_id=application.application_id,
                        document_type="BUREAU",
                        content=pdf_resp.content,
                        filename=f"bureau_report_{application.application_id}.pdf",
                        content_type="application/pdf",
                        subtype="bureau",
                    )
            except Exception as e:
                logger.error(f"Failed to download/upload bureau report for {application.application_id}: {str(e)}")

        # Generate a public/presigned URL for the response
        public_bureau_url = bureau_report_url
        if bureau_report_url:
            try:
                presigned = generate_presigned_get(
                    file_url=bureau_report_url,
                    response_headers={"response-content-disposition": "inline", "response-content-type": "application/pdf"}
                )
                public_bureau_url = presigned.get("get_url") or bureau_report_url
            except Exception:
                pass

        # Update application with bureau details
        try:
            application.bureau_score = int(credit_score_details.score_value) if credit_score_details.score_value else None
        except (ValueError, TypeError):
            application.bureau_score = None
        application.score_color = credit_score_details.score_color
        application.bureau_name = "EXPERIAN"
        application.bureau_pull_date = timezone.now().date()
        application.bureau_raw = data
        if bureau_report_url:
            application.bureau_report_link = bureau_report_url
        
        if result.get("overall_success"):
            application.bureau_decision = BureauDecision.APPROVED
        else:
            application.bureau_decision = BureauDecision.DECLINED
            application.status = ApplicationStatus.NOT_ELIGIBLE
        
        application.save(update_fields=[
            "bureau_score", "bureau_name", "bureau_pull_date", 
            "bureau_raw", "bureau_report_link", "bureau_decision", "status", "score_color", "modified_at"
        ])

        # Automatically persist eligibility stage data and mark as complete
        eligibility_payload = {
            "credit_bureau_url": public_bureau_url or pdf_url,
            "score_band": credit_score_details.score_band,
            "score_color": credit_score_details.score_color,
            "score_value": credit_score_details.score_value,
            "metadata": {"buearu_check_result": result}
        }
        persist_eligibility(application, eligibility_payload)
        save_stage_snapshot(application, ApplicationStage.ELIGIBILITY, eligibility_payload, True)
        update_application_progress(application, ApplicationStage.ELIGIBILITY, True, eligibility_payload)

        return JsonResponse({
            "status": True,
            "message": "Cibil check successfully completed",
            "data": {
                "score_band": credit_score_details.score_band,
                "score_color": credit_score_details.score_color,
                "score_value": credit_score_details.score_value,
                "credit_buearu_pdf_url": public_bureau_url or pdf_url,
                "credit_buearu_excel_url": excel_url,
                "buearu_check_result": result,
            }
        }, status=200)

    except Exception as exc:
        logger.exception(f"Experian bureau check failed for application {application.application_id}")
        return _mark_no_record_found_approved(
            application,
            {
                "status": False,
                "message": "Experian bureau check failed",
                "error": str(exc),
            },
        )

def run_bureau_check(api_response):
    results = []

    overall_success=True
    try:
      for validator in VALIDATORS:
          result = validator(api_response)
          results.append(result)
          if result.success == ValidationStatus.FAIL:
              overall_success = False
      return {
          "overall_success": True if overall_success else False,
          "results": [r.to_dict() for r in results]
      }
    except Exception as exc:
         return {"overall_success": False, "message": str(exc)}

def get_credit_score_details(score_value: Optional[str]) -> CreditScoreDetails:

    if score_value is None:
        return NO_SCORE
    try:
        score = int(score_value)
    except (TypeError, ValueError):
        return NO_SCORE

    if score < 0:
        return NO_SCORE

    try:
        result = (CreditScoreRange.objects
            .filter(min_score__lte=score, max_score__gte=score)
            .values("min_score", "max_score", "score_color", "score_band")
            .first())
    except Exception:
        return NO_SCORE

    if not result:
        return NO_SCORE

    return CreditScoreDetails(
        range=f"{result['min_score']}-{result['max_score']}",
        score_color=result["score_color"],
        score_band=result["score_band"],
        score_value=score_value)

def build_experian_payload(application):

            lead = application.lead
            pan_snap = _get_snapshot_payload(application, ApplicationStage.PAN)
            basic = _get_snapshot_payload(application, ApplicationStage.BASIC) or {}
            personal = _get_snapshot_payload(application, ApplicationStage.PERSONAL) or {}
            address = _get_snapshot_payload(application, ApplicationStage.ADDRESS) or {}
            missing = []

            if not pan_snap:
                missing.append("stage PAN not completed")
            if missing:
                raise ValueError(", ".join(missing))

            # PAN number
            pan_doc = ApplicationDocument.objects.filter(
                application=application, document_type="PAN"
            ).first()

            pan_number = pan_snap.get("pan_number")
            if not pan_number:
                missing.append("pan_number")

            # Name
            full_name =  pan_snap.get("name_on_pan") 
            first_name, last_name = _split_experian_name(full_name)
            if not first_name:
                missing.append("first_name")
            if not last_name:
                missing.append("last_name")

            # DOB
            dob =  pan_snap.get("dob_as_per_pan")
            if not dob:
                missing.append("DOB as per PAN")

            # Phone
            phone = pan_snap.get("contact_number")
            if not phone:
                missing.append("contact_number")

            # Pincode
            permanent = address.get("permanent") or {}
            pincode = permanent.get("pincode") or lead.pincode
            if not pincode:
                missing.append("pincode")

            if missing:
                 bureau_error("Missing required fields: " + ", ".join(missing))

            consent_ts = int(time.time())
            consent_ip = str(getattr(settings, "SIGNZY_CONSENT_IP", "") or "0.0.0.0")
            consent_msg_id = getattr(settings, "SIGNZY_CONSENT_MESSAGE_ID", None)
            if not consent_msg_id:
                # Signzy validates this against whitelisted/registered consent templates.
                 bureau_error("SIGNZY_CONSENT_MESSAGE_ID not configured; cannot trigger bureau check")
            consent_msg_id = str(consent_msg_id)

            phone_num = int(phone) if str(phone).isdigit() else phone

            payload = {
                "phoneNumber": phone_num,
                "pan": pan_number,
                "firstName": first_name,
                "lastName": last_name,
                "dateOfBirth": str(dob),
                "pincode": int(pincode) if str(pincode).isdigit() else pincode,
                "consent": {
                    "consentFlag": True,
                    "consentTimestamp": consent_ts,
                    "consentIpAddress": consent_ip,
                    "consentMessageId": consent_msg_id,
                },
            }
            return payload
