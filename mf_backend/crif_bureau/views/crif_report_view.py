from datetime import datetime
import logging
import re
import time
import uuid
from django.conf import settings
from requests import RequestException, Timeout
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from crif_bureau.models import CrifBureauReportTrace, CrifBureauTrace
from crif_bureau.serializer import PhoneToPanSerializer
from crif_bureau.serializer.crif_serializers import CrifReportSerializer
from crif_bureau.services.signzy_service import crif_report_request, phone_to_pan

logger = logging.getLogger(__name__)


def get_serializer_error(serializer):
    return str(next(iter(serializer.errors.values()), ["Invalid request."])[0])

def error_response_fallback(success, message, data=None, status_code=status.HTTP_200_OK,fallback=False):
        return Response({
            "success": success,
            "errors": message,
            "fallback": fallback
            },status=status_code)

def error_response(success, message, data=None, status_code=status.HTTP_200_OK):
        return Response({
            "success": success,
            "errors": message,
            },status=status_code)

def get_api_error(response):
    try:
        data = response.json()
        return data.get("error", {}).get("message", response.text)
    except Exception:
        return response.text


def get_client_ip(request):
    # x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    # if x_forwarded_for:
    #     return x_forwarded_for.split(",")[0].strip()
    # return request.META.get("REMOTE_ADDR")
    return "192.168.0.1"

def _get_pan_pro_payload(result,mobile_number):
    address = result.get("user_address", {})
    #Gender
    gender_code = result.get("user_gender", "").upper()
    gender_map = {
            "M": "Male",
            "F": "Female",
            "O": "Other"
            }
    gender = gender_map.get(gender_code, "Unknown")
    # Date of Birth (DD-MM-YYYY -> YYYY-MM-DD)
    dob = result.get("user_dob")
    formatted_dob = None
    if dob:
        try:
            formatted_dob = datetime.strptime(
            dob, "%d-%m-%Y"
            ).strftime("%Y-%m-%d")
        except ValueError:
            try:
                formatted_dob = datetime.strptime(
                dob, "%Y-%m-%d"
                ).strftime("%Y-%m-%d")
            except ValueError:
                formatted_dob = None
    # Address
    full_address = address.get("full")
    pin = address.get("zip") 
    pan_number = result.get("pan_number")
    full_name = result.get("user_full_name")
    payload={
            "phoneNumber": mobile_number,
            "address": full_address,
            "pincode": pin,
            "pan": pan_number,
            "firstName": full_name,
            "lastName": full_name,
            "dateOfBirth": formatted_dob,
            "gender": gender,
            "consent": {
                "consentFlag": True,
                "consentTimestamp": int(time.time()),
                "consentIpAddress": "49.36.112.25",
                "consentMessageId": "CM_1"
        }}
    return payload



HTTP_ERROR_MESSAGES = {
    400: {"message": "Missing or invalid request fields.","fallback": False},
    401: {"message": "Unauthorized access.","fallback": True},
    403: {"message": "Access denied or client is not whitelisted.","fallback": True},
    404: {"message": "Requested data was not found.","fallback": True},
    409: {"message": "Upstream dependency service is temporarily unavailable.","fallback": True},
    422: {"message": "Validation failed due to invalid or incomplete data.","fallback": True},
    429: {"message": "Rate limit exceeded. Please try again later.","fallback": True},
    500: {"message": "Internal server error.","fallback": True},
    502: {"message": "Bad gateway error from upstream service.","fallback": True},
    503: {"message": "Service temporarily unavailable.","fallback": True},
    504: {"message": "Upstream service request timed out.","fallback": True}
}

MINIMUM_CREDIT_SCORE=600

def _call_pan_pro(trace,pan_number,pan_holder_name,mobile_number):
            # 1. Call Zoop PAN verification API
            if not pan_holder_name:
                return error_response(False,"PAN holder name is required.",status.HTTP_400_BAD_REQUEST)
            if not mobile_number:
                return error_response(False,"Mobile number is required.",status.HTTP_400_BAD_REQUEST)

            task_id = str(uuid.uuid4())
            payload = {
                "mode": "sync",
                "data": {
                    "customer_pan_number": pan_number,
                    "pan_holder_name": pan_holder_name,
                    "consent": "Y",
                    "consent_text": "I hereby give my consent to verify my PAN details via Zoop API."
                },
                "task_id": task_id
            }
    
            headers = {
                "app-id": settings.ZOOP_APP_ID,
                "api-key": settings.ZOOP_API_KEY,
                "Content-Type": "application/json"
            }
    
            try:
                response = requests.post(settings.ZOOP_PAN_URL, json=payload, headers=headers)
                zoop_data = response.json()

                if zoop_data.get("response_code") != "100" or not zoop_data.get("success"):
                    error_msg = zoop_data.get("response_message") or zoop_data.get("message") or "Unknown error"
                    return error_response(False,error_msg,status.HTTP_400_BAD_REQUEST)
    
                result = zoop_data.get("result", {})
                user_phone_number = result.get("user_phone_number")

                if not user_phone_number:
                    return error_response(False,"Phone number not found",status.HTTP_400_BAD_REQUEST)

                # 2. Verify Mobile Number
                # Handles patterns like '90XXXXXX68'
                is_match = False
                clean_mobile_number = str(mobile_number).strip()
                clean_masked = str(user_phone_number).strip().upper()
    
                if len(clean_mobile_number) != 10:
                    return error_response(False,"Invalid Mobile number length. Expected 10 digits.",status.HTTP_400_BAD_REQUEST)
     
                # Create a regex pattern by replacing 'X' with '.'
                pattern = clean_masked.replace('X', '.')
                if re.fullmatch(pattern, mobile_number):
                    is_match = True

                
                if not is_match:
                    return error_response(False,"Mobile number does not match with the PAN.",status.HTTP_400_BAD_REQUEST)

                payload=_get_pan_pro_payload(result,mobile_number)
                #Crif Bureau report Api 
                return crif_bureau_report(trace,payload)
                
            except Exception as e:
                logger.exception("Mobile verification failed %s", str(e))
                return error_response(False,"Something went wrong. Please try again later.",status.HTTP_400_BAD_REQUEST)


def crif_bureau_report(trace,payload):
    try:
        send_response = crif_report_request(request_payload=payload)
    except (Timeout, RequestException) as exc:
            logger.warning("Something went wrong %s",str(exc))
            return error_response(False,"Something went wrong. Please try again.",status.HTTP_500_BAD_GATEWAY)
   
    send_data = send_response.json()
    trace.report_response_data = send_data
    trace.save(update_fields=["report_response_data"])
   
    if not (200 <= send_response.status_code < 300):
        trace.status = CrifBureauTrace.Status.FAILED
        trace.save()
        return error_response(
        False, 
        get_api_error(send_response) or "Something went wrong",
        status_code=send_response.status_code)
    
    try:
        credit_scores = (
            send_data.get("data", {})
            .get("crifReport", {})
            .get("INDV-REPORT-FILE", {})
            .get("INDV-REPORTS", [])[0]
            .get("INDV-REPORT", {})
            .get("SCORES", []))
        if credit_scores:
            credit_scores = int(credit_scores[0].get("SCORE-VALUE", 0))
        else:
            credit_scores=0
                    
    except Exception as e:
        credit_scores=0
        logger.warning("Error parsing decrypted webhook fields | error=%s", e)

    pdf_report_link = send_data.get("data", {}).get("crifPDF")
    logger.info("pdf url is ---> %s",pdf_report_link)
                    
    trace.pdf_report_link = pdf_report_link
    trace.score = credit_scores
    trace.status = CrifBureauReportTrace.FileDownloadStatus.COMPLETED
    trace.save(update_fields=["pdf_report_link", "score", "status", "modified_at"])
    
    if credit_scores < MINIMUM_CREDIT_SCORE:
        return Response({"success": False,
                   "message": f"We regret to inform you that your credit score of {credit_scores} does not meet the eligibility criteria at this time.",
                    "credit_score": credit_scores},
                    status=status.HTTP_200_OK)
    
    return Response({
            "success": True,
            "message":f"Great news! Your credit score of {credit_scores} has been successfully verified. You are eligible to proceed with the next step.",
            "credit_score": credit_scores},
            status=status.HTTP_200_OK)

class CrifReportView(APIView):
    serializer_class = PhoneToPanSerializer

    @extend_schema(request=PhoneToPanSerializer)
    def post(self, request):
        try:
            serializer = PhoneToPanSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    False, 
                    get_serializer_error(serializer),
                    status_code=status.HTTP_400_BAD_REQUEST)    
        
            validated = serializer.validated_data
            mobile_number = validated.get("phoneNumber")
            first_name = validated.get("firstName")
            last_name = validated.get("lastName")
            address = validated.get("address")
            pincode = validated.get("pincode")
            pan_number = validated.get("panNumber")

            # Create or update pre-lead trace log for step 1
            trace, _ = CrifBureauReportTrace.objects.update_or_create(
                    phone_number=mobile_number,
                    defaults={
                        "phone_to_pan_request": {
                        "phoneNumber": mobile_number,
                        "firstName": first_name,
                        "lastName": last_name,
                        "address": address,
                        "pincode": pincode,
                        },
                        "status": CrifBureauReportTrace.FileDownloadStatus.PENDING,
                    })
            
            if pan_number:
                try:
                   logger.error("pan pro tnrnjg ----->") 
                   return _call_pan_pro(trace=trace,pan_number=pan_number,pan_holder_name=first_name,mobile_number=mobile_number)
                except Exception as excp:
                    logger.error("pan pro error is -----> %s",str(excp))  
                    return Response({
                           "success": False,
                           "error": "Something went wrong. Please try again later."
                            },status=status.HTTP_400_BAD_REQUEST)
            
            else:
                try:
                    response = phone_to_pan(mobile_number=mobile_number, first_name=first_name, last_name=last_name)
                except (Timeout, RequestException) as exc:
                    logger.info("Fail to call phone_to_pan")
                    status_code=exc.response.status_code            
                    error_message=(exc.response.json().get("error", {}).get("message") 
                                or "Something went wrong while processing the request.").replace('"', '')
                    return error_response_fallback(
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
                    trace.phone_to_pan_response = {
                                        "error": "Failed to reach Signzy phone_to_pan API"}
                    trace.save()
                    status_code=response.status_code            
                    error_message=get_api_error(response) or "Something went wrong while processing the request."
                    return error_response_fallback(
                                        False,
                                        error_message,
                                        status_code=status_code,
                                        fallback=HTTP_ERROR_MESSAGES[status_code]["fallback"] if status_code in HTTP_ERROR_MESSAGES else False)
                    
            
                try:
                    response_block = data.get("response") or {}
                    personal_info = response_block.get("personalInfo") or {}
                    pan = response_block.get("pan")
                    if pan:
                        trace.pan_number = pan

                    trace.save(update_fields=["pan_number", "phone_to_pan_response", "modified_at"])
                    # def normalize_gender(personal_info):
                    #     gender = personal_info.get("gender")

                    #     if gender:
                    #         gender = gender.strip().capitalize()

                    gender = personal_info.get("gender", "").strip().capitalize()
                    date_of_birth=personal_info["dateOfBirth"]

                    name=personal_info["name"].strip().split()
                    first_name=name[0] if name else ""
                    last_name= " ".join(name[1:]) if len(name) > 1 else ""

                    payload={
                "phoneNumber": mobile_number,
                "address": address,
                "pincode": pincode,
                "pan": pan,
                "firstName": first_name,
                "lastName": last_name,
                "dateOfBirth": date_of_birth,
                "gender": gender,
                "consent": {
                    "consentFlag": True,
                    "consentTimestamp": int(time.time()),
                    "consentIpAddress": get_client_ip(request),
                    "consentMessageId": "CM_1"
                    }}
                    logger.info("crif report payload-----> %s",payload)
                except ValueError:
                    data = {"raw": response.text}

                trace.phone_to_pan_response = data
                trace.save(update_fields=["phone_to_pan_response", "modified_at"])

                send_serializer = CrifReportSerializer(data=payload)
                if not send_serializer.is_valid():
                      return error_response(
                      False, 
                      get_serializer_error(serializer),
                      status_code=status.HTTP_400_BAD_REQUEST)
                #Crif Bureau report Api 
                return crif_bureau_report(trace,payload)

        except Exception as exc:
            logger.error("crif report view error-----> %s",str(exc))
            return Response({
                "success": False,
                "error": f"Something went wrong. Please try again later."
                },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
