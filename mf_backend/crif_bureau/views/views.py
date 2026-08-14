import logging
from urllib.parse import urlparse

from django.conf import settings
from django.urls import reverse
from requests import RequestException, Timeout
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from crif_bureau.crif_automation_2 import automate
from crif_bureau.models import CrifBureauTrace
from crif_bureau.serializer import (
    PhoneToPanSerializer,
    SendCrifRequestSerializer,
    RequestDataSerializer,
    CrifWebhookSerializer)

from crif_bureau.services import (
    CrifBureauService,
    create_bureau_consent,
    phone_to_pan,
    send_crif_request)

logger = logging.getLogger(__name__)


CALLBACK_URL = settings.CRIF_CALLBACK_URL
REDIRECT_URL = settings.CRIF_REDIRECT_URL

def get_serializer_error(serializer):
    return str(next(iter(serializer.errors.values()), ["Invalid request."])[0])

def error_response(success, message, data=None, status_code=status.HTTP_200_OK,fallback=None):
        return Response(
            {
                "success": success,
                "errors": message,
                "fallback": fallback
            },
            status=status_code)

HTTP_ERROR_MESSAGES = {
    400: {"message": "Missing or invalid request fields.","fallback": False},
    401: {"message": "Unauthorized access.","fallback": False},
    403: {"message": "Access denied or client is not whitelisted.","fallback": False},
    404: {"message": "Requested data was not found.","fallback": False},
    409: {"message": "Upstream dependency service is temporarily unavailable.","fallback": True},
    422: {"message": "Validation failed due to invalid or incomplete data.","fallback": False},
    429: {"message": "Rate limit exceeded. Please try again later.","fallback": True},
    500: {"message": "Internal server error.","fallback": True},
    502: {"message": "Bad gateway error from upstream service.","fallback": True},
    503: {"message": "Service temporarily unavailable.","fallback": True},
    504: {"message": "Upstream service request timed out.","fallback": True}
}

def validate_public_https_url(url, setting_name):
    url = (url or "").strip().rstrip("/")
    if not url:
        raise ValueError(f"{setting_name} must be configured")

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"{setting_name} must be an absolute URL")
    if parsed.scheme != "https":
        raise ValueError(f"{setting_name} must use https")
    return url


def build_crif_callback_url(request, phone_number):
    """
    Build a Signzy-compatible callback URL.

    Signzy rejects some callback URLs when dynamic data is sent as a query
    parameter, so prefer the path-style webhook endpoint.
    """
    callback_base = (getattr(settings, "CRIF_CALLBACK_URL", None) or "").strip()
    if callback_base:
        callback_base = validate_public_https_url(callback_base, "CRIF_CALLBACK_URL")
        parsed = urlparse(callback_base)

        if callback_base.endswith(f"/{phone_number}"):
            return f"{callback_base}/"
        if callback_base.endswith("/webhook"):
            return f"{callback_base}/{phone_number}/"

        callback_path = reverse("crif_bureau_webhook_with_phone", kwargs={"phone_number": phone_number})
        if parsed.path in ("", "/"):
            return f"{callback_base}{callback_path}"
        return f"{callback_base}/{phone_number}/"

    callback_path = reverse("crif_bureau_webhook_with_phone", kwargs={"phone_number": phone_number})
    callback_url = request.build_absolute_uri(callback_path)
    parsed = urlparse(callback_url)
    if parsed.scheme != "https":
        raise ValueError("CRIF callback URL must be public https. Configure CRIF_CALLBACK_URL.")
    return callback_url


def build_crif_redirect_url():
    return validate_public_https_url(getattr(settings, "CRIF_REDIRECT_URL", None), "CRIF_REDIRECT_URL")

class PhoneToPanView(APIView):
    serializer_class = PhoneToPanSerializer

    @extend_schema(request=PhoneToPanSerializer)
    def post(self, request):
        serializer = PhoneToPanSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                False, 
                get_serializer_error(serializer),
                status_code=status.HTTP_400_BAD_REQUEST)    
        
        validated = serializer.validated_data
        mobile_number = validated.get("phoneNumber")
        full_name = validated.get("fullName")
        address = validated.get("address")
        pincode = validated.get("pincode")
        pan_number = validated.get("panNumber")

        if pan_number:
            #### Call PAN PRO API here 
            return Response(
                {
                    "success": True,
                    "message": "PAN number is provided. No need to call phone_to_pan API."
                },
                status=status.HTTP_200_OK)

        name_parts = (full_name or "").strip().split()
        first_name = name_parts[0] if name_parts else ""
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Create or update pre-lead trace log for step 1
        trace, _ = CrifBureauTrace.objects.update_or_create(
            phone_number=mobile_number,
            defaults={
                "phone_to_pan_request": {
                    "phoneNumber": mobile_number,
                    "fullName": full_name,
                    "address": address,
                    "pincode": pincode,
                },
                "status": CrifBureauTrace.Status.PENDING,
            }
        )

        try:
            response = phone_to_pan(mobile_number=mobile_number, first_name=first_name, last_name=last_name)
        except (Timeout, RequestException) as exc:
            trace.phone_to_pan_response = {
                "error": "Failed to reach Signzy phone_to_pan API",
                "details": str(exc)
            }
            trace.status = CrifBureauTrace.Status.FAILED
            trace.save()
            
            status_code=exc.response.status_code            
            error_message=(exc.response.json().get("error", {}).get("message") 
            or "Something went wrong while processing the request.").replace('"', '')
            
            return error_response(
                    False,
                    error_message
                    if status_code==400 else 
                    HTTP_ERROR_MESSAGES[status_code]["message"] if status_code in HTTP_ERROR_MESSAGES else "Failed to reach Signzy phone_to_pan API",
                    status_code=status_code,
                    fallback=HTTP_ERROR_MESSAGES[status_code]["fallback"] if status_code in HTTP_ERROR_MESSAGES else False)

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}

        trace.phone_to_pan_response = data
        trace.save(update_fields=["phone_to_pan_response", "modified_at"])

        if not (200 <= response.status_code < 300):
            trace.status = CrifBureauTrace.Status.FAILED
            trace.save(update_fields=["status", "modified_at"])
            return CrifBureauService.build_signzy_error_response(
                response,
                data,
                "Signzy phone_to_pan API returned an error")

        try:
            trace.phone_to_pan_response = data

            response_block = data.get("response") or {}
            personal_info = response_block.get("personalInfo") or {}
            pan = response_block.get("pan")
            if pan:
                trace.pan_number = pan
            trace.save(update_fields=["pan_number", "phone_to_pan_response", "modified_at"])

            gender=personal_info["gender"]
            date_of_birth=personal_info["dateOfBirth"]

            name=personal_info["name"].strip().split()
            first_name=name[0] if name else ""
            last_name= " ".join(name[1:]) if len(name) > 1 else ""

            try:
                dynamic_callback = build_crif_callback_url(request, mobile_number)
                redirect_url = build_crif_redirect_url()
            except ValueError as exc:
                trace.phone_to_pan_response["send_crif_error"] = str(exc)
                trace.status = CrifBureauTrace.Status.FAILED
                trace.save()

                return error_response(
                    False,
                    "Failed to build CRIF callback URL.",
                    status_code=status_code,
                    fallback=False)


            payload = { "phoneNumber": mobile_number,
                        "firstName": first_name,
                        "lastName": last_name,
                        "dateOfBirth": date_of_birth,
                        "panNumber": pan,
                        "gender": gender,
                        "address": address,
                        "pincode": pincode,
                        "callbackUrl": dynamic_callback,
                        "redirectUrl": redirect_url,
                        "productName": ["crif"],
                        "otpBypass": "true" }

        except ValueError:
            data = {"raw": response.text}
            trace.phone_to_pan_response = data
            trace.status = CrifBureauTrace.Status.FAILED
            trace.save(update_fields=["phone_to_pan_response", "status", "modified_at"])

        if 200 <= response.status_code < 300:
            send_serializer = SendCrifRequestSerializer(data=payload)
            if not send_serializer.is_valid():
                trace.phone_to_pan_response["send_crif_error"] = "SendCrifRequestSerializer validation failed"
                trace.status = CrifBureauTrace.Status.FAILED
                trace.save()
                return Response(
                    {
                        "success": False,
                        "error": "phone_to_pan succeeded but send_crif_request input is invalid."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            send_payload = send_serializer.validated_data.copy()
            send_payload, missing_fields = CrifBureauService.enrich_payload_with_phone_data(send_payload, data)
            if missing_fields:
                trace.phone_to_pan_response["send_crif_error"] = f"Missing enrichment fields: {missing_fields}"
                trace.status = CrifBureauTrace.Status.FAILED
                trace.save()
                return Response(
                    {
                        "success": False,
                        "error": "phone_to_pan succeeded but send_crif_request fields are missing after enrichment.",
                        "missing_fields": missing_fields,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                trace.phone_to_pan_response["send_crif_payload"] = payload
                trace.save()

                send_response = send_crif_request(request_payload=payload)
                send_response.raise_for_status() # Bugfix: call send_response.raise_for_status() instead of response.raise_for_status()

            except (Timeout, RequestException) as exc:
                trace.phone_to_pan_response["send_crif_error"] = {
                    "message": "Failed to reach Signzy send_crif_request API",
                    "details": str(exc)
                }
                trace.status = CrifBureauTrace.Status.FAILED
                trace.save()
                return Response(
                    {
                        "success": False,
                        "error": "phone_to_pan succeeded but failed to reach Signzy send_crif_request API",
                        "phone_to_pan_data": data,
                        "details": str(exc),
                    },
                    status=status.HTTP_502_BAD_GATEWAY)
            
            send_data = send_response.json()
            trace.phone_to_pan_response["send_crif_response"] = send_data
            trace.save()

            encrypted = send_data.get("encryptedData")
            if not (200 <= send_response.status_code < 300):
                trace.status = CrifBureauTrace.Status.FAILED
                trace.save()
                return Response(
                    {
                        "success": False,
                        "error": "phone_to_pan succeeded but Signzy send_crif_request API returned an error"
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            return Response(
                {"success": True, "encryptedData": encrypted},
                status=status.HTTP_200_OK,
            )

        return CrifBureauService.build_signzy_error_response(
            response,
            data,
            "Signzy phone_to_pan API returned an error")


class CreateBureauConsentView(APIView):
    serializer_class = RequestDataSerializer

    @extend_schema(request=RequestDataSerializer)
    def post(self, request):
        serializer = RequestDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": get_serializer_error(serializer)},
                status=status.HTTP_400_BAD_REQUEST)
        validated = serializer.validated_data
        request_data = validated["requestData"]

        # Attempt to resolve the phone number by decrypting the incoming requestData
        phone_number = None
        trace = None
        try:
            decrypted_req, _ = CrifBureauService.decrypt_signzy_payload(request_data=request_data)
            if decrypted_req and isinstance(decrypted_req, dict):
                phone_number = decrypted_req.get("phoneNumber")
        except Exception as e:
            logger.warning("Could not decrypt incoming requestData | error=%s", e)

        if phone_number:
            trace = CrifBureauTrace.objects.filter(phone_number=phone_number).first()

        if trace:
            trace.consent_request = {"requestData": request_data}
            trace.save(update_fields=["consent_request", "modified_at"])

        try:
            response = create_bureau_consent(request_data=request_data)
        except (Timeout, RequestException) as exc:
            if trace:
                trace.consent_response = {
                    "error": "Failed to reach Signzy create-bureau-consent API",
                    "details": str(exc)
                }
                trace.status = CrifBureauTrace.Status.FAILED
                trace.save()
            return Response({"success": False,
                             "error": "Failed to reach Signzy create-bureau-consent API",
                             "details": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY)
        redirect_url=""
        automation_result = None
        crif_score = None
        try:
            data = response.json()
            response_data = data.get("responseData") or {}
            decrypted_data, error_response = CrifBureauService.decrypt_signzy_payload(request_data=response_data)
            if error_response:
                if trace:
                    trace.consent_response = {
                        "error": "Failed to decrypt responseData",
                        "responseData": response_data
                    }
                    trace.status = CrifBureauTrace.Status.FAILED
                    trace.save()
                return error_response
            
            redirect_url=decrypted_data.get("result").get("url")
            if redirect_url:
                logger.info("Starting CRIF automation | url=%s", redirect_url)
                automation_result = automate(
                    redirect_url,
                    headless=True,
                    expected_redirect_url=getattr(settings, "CRIF_REDIRECT_URL", None),
                )

                if automation_result.get("success"):
                    crif_score = automation_result.get("crif_score")

                print("\n── Result ──────────────────────────────")
                if automation_result.get("success"):
                    print(f"  ✓ CRIF Score : {automation_result.get('crif_score')}")
                    print(f"  ✓ Final URL  : {automation_result.get('final_url')}")
                else:
                    print(f"  ✗ Error      : {automation_result.get('error')}")

            if trace:
                trace.consent_response = {
                    "raw_response": data,
                    "decrypted_data": decrypted_data,
                    "redirect_url": redirect_url,
                    "automation_result": automation_result,
                }
                update_fields = ["consent_response", "modified_at"]
                if crif_score is not None:
                    trace.score = crif_score
                    trace.status = CrifBureauTrace.Status.COMPLETED
                    update_fields.extend(["score", "status"])
                trace.save(update_fields=update_fields)

        except ValueError:
            data = {"raw": response.text}
            if trace:
                trace.consent_response = data
                trace.status = CrifBureauTrace.Status.FAILED
                trace.save()

        if 200 <= response.status_code < 300:
            return Response(
                {
                    "success": True,
                    "data": {
                        "redirect_url": redirect_url,
                        "crif_score": crif_score,
                        "automation": automation_result,
                    },
                },
                status=status.HTTP_200_OK)

        if trace:
            trace.status = CrifBureauTrace.Status.FAILED
            trace.save()

        return Response(
            {
                "success": False,
                "error": "Signzy create-bureau-consent API returned an error",
                "status_code": response.status_code
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )


class CrifBureauWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = CrifWebhookSerializer

    @extend_schema(
        request=CrifWebhookSerializer,
        parameters=[
            OpenApiParameter(
                name="phone_number",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="The customer phone number linked to the CRIF check.",
            ),
            OpenApiParameter(
                name="X-Saas-Token",
                type=str,
                location=OpenApiParameter.HEADER,
                required=False,
                description="Security verification token.",
            ),
        ],
        examples=[
            OpenApiExample(
                name="CRIF Webhook Payload",
                value={
                    "requestData": "U2FsdGVkX19z...encrypted_data_block..."
                },
                request_only=True,
            )
        ]
    )
    def post(self, request, phone_number=None):
        logger.info("CRIF bureau webhook received | payload=%s", request.data)

        # 1. Token Security Validation
        expected_token = getattr(settings, "CRIF_WEBHOOK_SECRET", None)
        provided_token = request.headers.get("X-Saas-Token")
        if expected_token and expected_token != provided_token:
            logger.warning("CRIF Webhook token mismatch | provided=%s", provided_token)
            return Response(
                {"success": False, "error": "Invalid webhook token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. Extract phone number from path or query parameters.
        phone_number = phone_number or request.query_params.get("phone_number")
        if not phone_number:
            logger.error("CRIF Webhook missing phone_number in query parameters")
            return Response(
                {"success": False, "error": "phone_number parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve or initialize trace entry
        trace = CrifBureauTrace.objects.filter(phone_number=phone_number).first()
        if not trace:
            logger.warning("No CrifBureauTrace entry found for phone_number=%s", phone_number)
            trace = CrifBureauTrace(phone_number=phone_number)

        trace.webhook_payload = request.data
        trace.save()

        # 3. Extract requestData from payload
        request_data = CrifBureauService.extract_request_data_from_payload(request.data)
        if not request_data:
            serializer = CrifWebhookSerializer(data=request.data)
            if not serializer.is_valid():
                trace.status = CrifBureauTrace.Status.FAILED
                trace.save()
                return Response(
                    {"success": False, "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request_data = serializer.validated_data.get("requestData")

        if not request_data:
            trace.status = CrifBureauTrace.Status.FAILED
            trace.save()
            return Response(
                {
                    "success": False,
                    "error": "requestData is required in webhook payload.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4. Decrypt raw Signzy data
        decrypted_data, error_response = CrifBureauService.decrypt_signzy_payload(request_data=request_data)
        if error_response:
            trace.status = CrifBureauTrace.Status.FAILED
            trace.decrypted_webhook_data = {"error": "Decryption failed", "response": error_response.data if hasattr(error_response, "data") else str(error_response)}
            trace.save()
            return error_response

        # 5. Extract score and complete state trace
        trace.decrypted_webhook_data = decrypted_data
        
        score = None
        pan = None
        reference_number = None
        pdf_report_link = None

        try:
            result_block = decrypted_data.get("result") or decrypted_data.get("response") or decrypted_data or {}
            if isinstance(result_block, dict):
                score = result_block.get("score") or result_block.get("crifScore")
                pan = result_block.get("pan") or result_block.get("panNumber") or result_block.get("pan_number")
                reference_number = result_block.get("referenceNumber") or result_block.get("enquiryNumber") or result_block.get("crifRefNo") or result_block.get("bureauReferenceNumber")
                pdf_report_link = result_block.get("pdfPath") or result_block.get("reportPath") or result_block.get("pdfReport") or result_block.get("pdfUrl")
        except Exception as e:
            logger.warning("Error parsing decrypted webhook fields | error=%s", e)

        if score is not None:
            try:
                trace.score = int(score)
            except (ValueError, TypeError):
                pass

        if pan:
            trace.pan_number = pan

        if reference_number:
            trace.reference_number = reference_number

        if pdf_report_link:
            trace.pdf_report_link = pdf_report_link

        trace.status = CrifBureauTrace.Status.COMPLETED
        trace.save()

        logger.info("CRIF bureau webhook successfully processed for phone_number=%s | score=%s", phone_number, score)

        return Response(
            {
                "success": True,
                "phone_number": phone_number,
                "score": score,
                "decrypted_data": decrypted_data,
            },
            status=status.HTTP_200_OK)
