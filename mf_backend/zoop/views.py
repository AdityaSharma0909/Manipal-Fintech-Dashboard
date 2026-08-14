import requests
import base64
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PanVerification, BankVerification, FaceMatchVerification
from .serializers import (
    PanVerificationSerializer, PanVerificationRequestSerializer,
    BankVerificationSerializer, DrivingLicenceVerificationSerializer,
    ChequeOCRVerificationSerializer,OCRLiteVerificationSerializer,
    VoterIDAdvanceVerificationSerializer,PassportAdvanceVerificationSerializer,
    FaceMatchVerificationSerializer, FaceMatchRequestSerializer
)
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from tasks.models import SubTaskTracker
from django.core.cache import cache
import random
from users.service.otpService import OtpService
from users.models import UserOtp
from utils.constants import OTP_TYPE
from django.db.models import Q

#  Common helper to handle Zoop API responses
def handle_zoop_response(api_data, serializer=None, success_message="Verification successful"):
    response_code = api_data.get("response_code")
    success = api_data.get("success", False)
    message = api_data.get("response_message", "")

    if response_code == "100" and success:
        return Response({
            "status": "success",
            "message": success_message,
            "data": api_data
        }, status=status.HTTP_200_OK)

    elif response_code == "104":
        return Response({
            "status": "error",
            "message": "Missing or invalid consent text. Consent text must be at least 20 characters.",
            "api_response": api_data
        }, status=status.HTTP_400_BAD_REQUEST)

    elif response_code == "106":
        return Response({
            "status": "error",
            "message": "Invalid ID number or combination of inputs.",
            "api_response": api_data
        }, status=status.HTTP_400_BAD_REQUEST)

    elif response_code == "108":
        return Response({
            "status": "error",
            "message": "Source error occurred at data provider.",
            "api_response": api_data
        }, status=status.HTTP_502_BAD_GATEWAY)

    elif response_code == "109":
        return Response({
            "status": "error",
            "message": "Source timed out. Please try again later.",
            "api_response": api_data
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)

    else:
        return Response({
            "status": "error",
            "message": f"Unexpected response from Zoop API: {response_code or 'Unknown'}",
            "api_response": api_data
        }, status=status.HTTP_400_BAD_REQUEST)


#  PAN Verification
class PanVerificationAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PanVerificationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        pan_number = data["customer_pan_number"]
        pan_holder_name = data["pan_holder_name"]
        task_id = str(uuid.uuid4())
        sub_task_tracker_id = data.get("sub_task_tracker_id")
        print("Payload Data:", data)

        #  Hybrid consent handling
        consent_text = data.get(
            "consent_text",
            "I hereby give my consent to verify my PAN details via Zoop API."
        )

        payload = {
            "mode": "sync",
            "data": {
                "customer_pan_number": pan_number,
                "pan_holder_name": pan_holder_name,
                "consent": "Y",
                "consent_text": consent_text
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
            data = response.json()

            meta = data.get('metadata', {})
            result = data.get('result', {})

            pan_obj = PanVerification.objects.create(
                request_id=data.get('request_id'),
                task_id=data.get('task_id'),
                group_id=data.get('group_id'),
                response_code=data.get('response_code'),
                response_message=data.get('response_message'),
                billable=meta.get('billable'),
                pan_number=result.get('pan_number') if result else pan_number,
                pan_holder_name=result.get('user_full_name') if result else pan_holder_name,
                name_match_score=result.get('name_match_score') if result else None,
                pan_type=result.get('pan_type') if result else None,
                aadhaar_linked_status=result.get('aadhaar_linked_status') if result else False,
                masked_aadhaar=result.get('masked_aadhaar') if result else None,
                user_email=result.get('user_email') if result else None,
                user_phone_number=result.get('user_phone_number') if result else None,
                user_gender=result.get('user_gender') if result else None,
                user_dob=result.get('user_dob') if result else None,
                user_address=result.get('user_address') if result else None,
                request_timestamp=data.get('request_timestamp'),
                response_timestamp=data.get('response_timestamp')
            )

            # Update SubTaskTracker if sub_task_tracker_id is provided and verification successful
            if sub_task_tracker_id and data.get('response_code') == '100':
                try:
                    tracker = SubTaskTracker.objects.get(id=sub_task_tracker_id)
                    tracker.is_pan_verify = True
                    tracker.pan_number = pan_number
                    tracker.is_zoop_pan_verify = True
                    tracker.modified_by = request.user
                    tracker.save(update_fields=['is_pan_verify', 'is_zoop_pan_verify', 'pan_number', 'modified_by', 'modified_at'])
                except SubTaskTracker.DoesNotExist:
                    pass

            return handle_zoop_response(data, serializer=PanVerificationSerializer(pan_obj))

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  Bank Verification
# class BankVerificationView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         serializer = BankVerificationSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         data = serializer.validated_data
#         task_id = str(uuid.uuid4())

#         #  Hybrid consent handling
#         consent_text = data.get(
#             "consent_text",
#             "I hereby give my consent to verify my bank account details via Zoop API."
#         )

#         payload = {
#             "mode": "sync",
#             "data": {
#                 "account_number": data["account_number"],
#                 "ifsc": data["ifsc"],
#                 "consent": "Y",
#                 "name_to_match": data["name_to_match"],
#                 "consent_text": consent_text
#             },
#             "task_id": task_id
#         }

#         headers = {
#             "Content-Type": "application/json",
#             "app-id": settings.ZOOP_APP_ID,
#             "api-key": settings.ZOOP_API_KEY
#         }

#         try:
#             response = requests.post(settings.ZOOP_BANK_VERIFICATION_URL, json=payload, headers=headers)
#             api_data = response.json()

#             if response.status_code == 200:
#                 result = api_data.get("result", {}) or {}
#                 ifsc_info = result.get("ifscDetails", {}) or {}

#                 serializer.save(
#                     request_id=api_data.get("request_id"),
#                     group_id=api_data.get("group_id"),
#                     success=api_data.get("success", False),
#                     response_code=api_data.get("response_code"),
#                     response_message=api_data.get("response_message"),
#                     beneficiary_name=result.get("beneficiary_name"),
#                     verification_status=result.get("verification_status"),
#                     name_match_score=result.get("name_match_score"),
#                     transaction_remark=result.get("transaction_remark"),
#                     bank_name=ifsc_info.get("name"),
#                     branch=ifsc_info.get("branch"),
#                     state=ifsc_info.get("state"),
#                     city=ifsc_info.get("city"),
#                     address=ifsc_info.get("address"),
#                 )

#                 return handle_zoop_response(api_data, serializer, "Bank account verified successfully")

#             else:
#                 return Response({
#                     "status": "error",
#                     "message": "Zoop API returned non-200 response",
#                     "api_response": api_data
#                 }, status=response.status_code)

#         except Exception as e:
#             return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BankVerificationView(APIView):
    
    permission_classes = []

    def post(self, request):
        serializer = BankVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        task_id = str(uuid.uuid4())

        # Hybrid consent handling
        consent_text = data.get(
            "consent_text",
            "I hereby give my consent to verify my bank account details via Zoop API."
        )

        payload = {
            "mode": "sync",
            "data": {
                "account_number": data["account_number"],
                "ifsc": data["ifsc"],
                "consent": "Y",
                "name_to_match": data["name_to_match"],
                "consent_text": consent_text
            },
            "task_id": task_id
        }

        headers = {
            "Content-Type": "application/json",
            "app-id": settings.ZOOP_APP_ID,
            "api-key": settings.ZOOP_API_KEY
        }

        try:
            response = requests.post(settings.ZOOP_BANK_VERIFICATION_URL, json=payload, headers=headers)
            api_data = response.json()

            if response.status_code == 200:
                result = api_data.get("result", {}) or {}
                ifsc_info = result.get("ifscDetails", {}) or {}

                # Penny-drop fields from Zoop response
                is_penny_drop = result.get("is_penny_drop", False)
                penny_drop_amount = result.get("penny_drop_amount")
                penny_drop_txn_ref = result.get("transaction_ref")

                serializer.save(
                    request_id=api_data.get("request_id"),
                    group_id=api_data.get("group_id"),
                    success=api_data.get("success", False),
                    response_code=api_data.get("response_code"),
                    response_message=api_data.get("response_message"),
                    beneficiary_name=result.get("beneficiary_name"),
                    verification_status=result.get("verification_status"),
                    name_match_score=result.get("name_match_score"),
                    transaction_remark=result.get("transaction_remark"),
                    bank_name=ifsc_info.get("name"),
                    branch=ifsc_info.get("branch"),
                    state=ifsc_info.get("state"),
                    city=ifsc_info.get("city"),
                    address=ifsc_info.get("address"),
                    # Save penny-drop info
                    is_penny_drop=is_penny_drop,
                    penny_drop_amount=penny_drop_amount,
                    penny_drop_txn_ref=penny_drop_txn_ref
                )

                return handle_zoop_response(api_data, serializer, "Bank account verified successfully")

            else:
                return Response({
                    "status": "error",
                    "message": "Zoop API returned non-200 response",
                    "api_response": api_data
                }, status=response.status_code)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#  Driving Licence Verification
class DrivingLicenceVerificationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = DrivingLicenceVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        task_id = str(uuid.uuid4())

        # Hybrid consent handling
        consent_text = data.get(
            "consent_text",
            "I hereby give my consent to verify my driving licence details via Zoop API."
        )

        payload = {
            "mode": "sync",
            "data": {
                "customer_dl_number": data["customer_dl_number"],
                "name_to_match": data["name_to_match"],
                "customer_dob": data["customer_dob"],
                "consent": "Y",
                "consent_text": consent_text,
            },
            "task_id": task_id
        }

        headers = {
            "Content-Type": "application/json",
            "app-id": settings.ZOOP_APP_ID,
            "api-key": settings.ZOOP_API_KEY,
        }

        try:
            response = requests.post(settings.ZOOP_DL_URL, json=payload, headers=headers)
            api_data = response.json()

            # make result extraction robust (support result or data)
            result = api_data.get("result") or api_data.get("data") or {}
            address_info = (result.get("user_address") or [{}])[0]

            # save response along with task_id and consent_text for audit
            serializer.save(
                task_id=task_id,
                request_id=api_data.get("request_id"),
                group_id=api_data.get("group_id"),
                success=api_data.get("success", False),
                response_code=api_data.get("response_code"),
                response_message=api_data.get("response_message"),
                user_full_name=result.get("user_full_name"),
                user_dob=result.get("user_dob"),
                father_or_husband=result.get("father_or_husband"),
                dl_number=result.get("dl_number"),
                expiry_date=result.get("expiry_date"),
                user_blood_group=result.get("user_blood_group"),
                status=result.get("status"),
                name_match_score=result.get("name_match_score"),
                state=result.get("state"),
                address=address_info.get("completeAddress"),
                pin=address_info.get("pin"),
                district=address_info.get("district"),
                address_type=address_info.get("type"),
                consent_text=consent_text  # persist the consent text
            )

            # reuse your centralized response handler (unchanged)
            return handle_zoop_response(api_data, serializer, "Driving Licence verified successfully")

        except requests.RequestException as e:
            return Response({
                "status": "error",
                "message": f"Error while connecting to Zoop API: {str(e)}"
            }, status=status.HTTP_502_BAD_GATEWAY)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Cheque OCR Verification
class ChequeOCRVerificationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ChequeOCRVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        task_id = str(uuid.uuid4())

        #  Read uploaded cheque image file and convert to Base64
        cheque_file = request.FILES.get("cheque_image")
        if not cheque_file:
            return Response({
                "status": "error",
                "message": "Please upload a cheque image file."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            cheque_file.seek(0)
            cheque_image_base64 = base64.b64encode(cheque_file.read()).decode('utf-8')
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error reading image file: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        consent_text = data.get(
            "consent_text",
            "I hereby give my consent to verify my cheque details via Zoop API."
        )

        payload = {
            "mode": "sync",
            "data": {
                "cheque_image": cheque_image_base64,
                "consent": "Y",
                "consent_text": consent_text,
            },
            "task_id": task_id,
        }

        headers = {
            "Content-Type": "application/json",
            "app-id": settings.ZOOP_APP_ID,
            "api-key": settings.ZOOP_API_KEY,
        }

        try:
            response = requests.post(settings.ZOOP_CHEQUE_OCR_URL, json=payload, headers=headers)
            api_data = response.json()

            result = api_data.get("result", {}) or {}
            branch_details = result.get("branch_details", {}) or {}

            serializer.save(
                request_id=api_data.get("request_id"),
                task_id=api_data.get("task_id"),
                group_id=api_data.get("group_id"),
                success=api_data.get("success", False),
                response_code=api_data.get("response_code"),
                response_message=api_data.get("response_message"),
                bank=result.get("bank"),
                ifsc_code=result.get("ifsc_code"),
                account_number=result.get("account_number"),
                branch=branch_details.get("branch"),
                city=branch_details.get("city"),
                state=branch_details.get("state"),
                request_timestamp=api_data.get("request_timestamp"),
                response_timestamp=api_data.get("response_timestamp"),
            )

            return handle_zoop_response(api_data, serializer, "Cheque OCR verified successfully")

        except requests.RequestException as e:
            return Response({
                "status": "error",
                "message": f"Error while connecting to Zoop API: {str(e)}"
            }, status=status.HTTP_502_BAD_GATEWAY)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
# OCR Lite Verification
class OCRLiteVerificationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = OCRLiteVerificationSerializer(data=request.data)
        if serializer.is_valid():
            sub_task_tracker_id = serializer.validated_data.pop('sub_task_tracker_id', None)
            
            serializer.save()

            card_front_file = request.FILES.get('card_front_image')
            card_back_file = request.FILES.get('card_back_image')
            card_type = serializer.validated_data.get('card_type', 'PAN').upper()
            consent = serializer.validated_data.get('consent', 'Y')
            consent_text = serializer.validated_data.get(
                'consent_text',
                'I hereby give my consent to verify my document via Zoop.'
            )

            # ✅ Supported card types list
            supported_cards = ["PAN", "AADHAAR", "DRIVING_LICENSE", "VOTER_ID", "PASSPORT", "OTHER"]
            if card_type not in supported_cards:
                return Response({
                    "status": "error",
                    "message": f"Unsupported card type '{card_type}'. Supported types are: {', '.join(supported_cards)}."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Convert file to base64
            def file_to_base64(file):
                if not file:
                    return None
                file.seek(0)
                return base64.b64encode(file.read()).decode('utf-8')

            payload = {
                "mode": "sync",
                "data": {
                    "card_front_image": file_to_base64(card_front_file),
                    "card_back_image": file_to_base64(card_back_file),
                    "card_type": card_type,
                    "consent": consent,
                    "consent_text": consent_text,
                },
                "task_id": serializer.validated_data.get("task_id") or str(uuid.uuid4()),
            }

            headers = {
                "Content-Type": "application/json",
                "app-id": settings.ZOOP_APP_ID,
                "api-key": settings.ZOOP_API_KEY,
            }

            zoop_url = settings.ZOOP_OCR_LITE_URL
            response = requests.post(zoop_url, json=payload, headers=headers)
            print("Zoop OCR Lite Response Status:", response.status_code)
            print("Zoop OCR Lite Response Text:", response.text)

            try:
                api_data = response.json()
            except ValueError:
                return Response({
                    "status": "error",
                    "message": "Invalid or empty response from Zoop API",
                    "raw_response": response.text
                }, status=response.status_code)

            # Update SubTaskTracker based on card type
            if sub_task_tracker_id and api_data.get('response_code') == '100':
                try:
                    tracker = SubTaskTracker.objects.get(id=sub_task_tracker_id)
                    result = api_data.get('result', {})
                    card_info = result.get('card_info', {})
                    
                    # Handle AADHAAR
                    if card_type == 'AADHAAR' and card_info:
                        aadhar_number = card_info.get('card_number')
                        if aadhar_number:
                            tracker.is_aadhar_verify = True
                            tracker.aadhar_number = aadhar_number
                            tracker.modified_by = request.user
                            tracker.save(update_fields=[
                                'is_aadhar_verify', 'aadhar_number', 'modified_by', 'modified_at'
                            ])
                            print(f"✅ Aadhaar verified for tracker {tracker.id}")
                    
                    # Handle OTHER DOCUMENTS (Driving License, Passport, Voter ID)
                    elif card_type in ['DRIVING_LICENSE', 'VOTER_ID', 'PASSPORT'] and card_info:
                        document_number = card_info.get('card_number') or card_info.get('id_number')
                        if document_number:
                            tracker.other_document_verified = True
                            tracker.other_document = card_type  # Store which document was verified
                            tracker.modified_by = request.user
                            tracker.save(update_fields=[
                                'other_document_verified', 'other_document', 'modified_by', 'modified_at'
                            ])
                            print(f"✅ {card_type} verified for tracker {tracker.id}")
                    
                except SubTaskTracker.DoesNotExist:
                    print(f"❌ Tracker {sub_task_tracker_id} not found")
                except Exception as e:
                    print(f"❌ Error updating tracker: {str(e)}")
                    import traceback
                    traceback.print_exc()

            return handle_zoop_response(api_data, serializer, "OCR Lite verified successfully")

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VoterIDAdvanceVerificationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = VoterIDAdvanceVerificationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        task_id = str(uuid.uuid4())

        consent_text = data.get(
            "consent_text",
            "I hereby declare my consent agreement for fetching my information via ZOOP API."
        )

        payload = {
            "data": {
                "customer_epic_number": data["customer_epic_number"],
                "name_to_match": data["name_to_match"],
                "consent": "Y",
                "consent_text": consent_text,
            },
            "task_id": task_id
        }

        headers = {
            "Content-Type": "application/json",
            "app-id": settings.ZOOP_APP_ID,
            "api-key": settings.ZOOP_API_KEY
        }

        try:
            response = requests.post(settings.ZOOP_VOTER_ADVANCE_URL, json=payload, headers=headers)
            api_data = response.json()

            result = api_data.get("result", {}) or {}

            # SAVE ONLY FIELDS THAT EXIST IN YOUR MODEL
            serializer.save(
                task_id=task_id,
                request_id=api_data.get("request_id"),
                group_id=api_data.get("group_id"),
                success=api_data.get("success", False),
                response_code=api_data.get("response_code"),
                response_message=api_data.get("response_message"),

                # Result fields
                user_name_english=result.get("user_name_english"),
                user_name_vernacular=result.get("user_name_vernacular"),
                user_gender=result.get("user_gender"),
                user_age=result.get("user_age"),

                relative_name_english=result.get("relative_name_english"),
                relative_name_vernacular=result.get("relative_name_vernacular"),
                relative_relation=result.get("relative_relation"),

                assembly_constituency_name=result.get("assembly_constituency_name"),
                constituency_part_number=result.get("constituency_part_number"),
                serial_number_applicable_part=result.get("serial_number_applicable_part"),
                status=result.get("status"),

                voter_last_updated_date=result.get("voter_last_updated_date"),
            )

            return handle_zoop_response(api_data, serializer, "Voter ID verified successfully")

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)


class PassportAdvanceVerificationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = PassportAdvanceVerificationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        task_id = str(uuid.uuid4())

        # Build Zoop Payload
        payload = {
            "mode": "sync",
            "data": {
                "customer_file_number": data["customer_file_number"],
                "name_to_match": data["name_to_match"],
                "customer_dob": data["customer_dob"],
                "consent": "Y",
                "consent_text": data.get(
                    "consent_text",
                    "I hereby declare my consent agreement for fetching my information via ZOOP API"
                )
            },
            "task_id": task_id
        }

        headers = {
            "Content-Type": "application/json",
            "app-id": settings.ZOOP_APP_ID,
            "api-key": settings.ZOOP_API_KEY
        }

        # Call Zoop API
        response = requests.post(
            settings.ZOOP_PASSPORT_ADVANCE_URL,
            json=payload,
            headers=headers
        )
        api_data = response.json()
        result = api_data.get("result", {}) or {}

        # Save to DB
        serializer.save(
            task_id=task_id,
            request_id=api_data.get("request_id"),
            group_id=api_data.get("group_id"),
            success=api_data.get("success"),
            response_code=api_data.get("response_code"),
            response_message=api_data.get("response_message"),

            passport_status=result.get("passport_satus"),  # ZOOP typo
            name_on_passport=result.get("name_on_passport"),
            customer_last_name=result.get("customer_last_name"),
            passport_number=result.get("passport_number"),
            passport_applied_date=result.get("passport_applied_date"),
            name_match_score=result.get("name_match_score"),
            customer_dob_result=result.get("customer_dob"),
        )

        return handle_zoop_response(api_data, serializer, "Passport verified successfully")


class FaceMatchVerificationAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = FaceMatchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        task_id = str(uuid.uuid4())
        sub_task_tracker_id = data.get("sub_task_tracker_id")

        payload = {
            "mode": "sync",
            "data": {
                "card_image": data["card_image"],
                "user_image": data["user_image"],
                "consent": data.get("consent", "Y"),
                "consent_text": data.get("consent_text", "I hereby declare my consent agreement for fetching my information via ZOOP API")
            },
            "task_id": task_id
        }

        headers = {
            "app-id": settings.ZOOP_APP_ID,
            "api-key": settings.ZOOP_API_KEY,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(settings.ZOOP_FACE_MATCH_URL, json=payload, headers=headers)
            api_data = response.json()

            meta = api_data.get('metadata', {})
            result = api_data.get('result', {})

            face_match_obj = FaceMatchVerification.objects.create(
                card_image=data["card_image"],
                user_image=data["user_image"],
                consent=data.get("consent", "Y"),
                consent_text=data.get("consent_text"),
                task_id=api_data.get('task_id', task_id),
                request_id=api_data.get('request_id'),
                group_id=api_data.get('group_id'),
                success=api_data.get('success', False),
                response_code=api_data.get('response_code'),
                response_message=api_data.get('response_message'),
                billable=meta.get('billable'),
                reason_message=meta.get('reason_message'),
                face_match_score=result.get('face_match_score') if result else None,
                request_timestamp=api_data.get('request_timestamp'),
                response_timestamp=api_data.get('response_timestamp')
            )

            # Update SubTaskTracker if sub_task_tracker_id is provided and verification successful
            if sub_task_tracker_id and api_data.get('response_code') == '100':
                try:
                    tracker = SubTaskTracker.objects.get(id=sub_task_tracker_id)
                    # Check if tracker has is_face_match_verify field
                    if hasattr(tracker, 'is_face_match_verify'):
                        tracker.is_face_match_verify = True
                        tracker.modified_by = request.user
                        tracker.save(update_fields=['is_face_match_verify', 'modified_by', 'modified_at'])
                except SubTaskTracker.DoesNotExist:
                    pass
                except Exception as e:
                    print(f"Error updating tracker: {e}")

            return handle_zoop_response(api_data, serializer=FaceMatchVerificationSerializer(face_match_obj), success_message="Face match successful")

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# SMS OTP API INTEGRATIONS


def send_sms_otp(mobile_number, otp):
    """
    Send OTP SMS using SMSGatewayHub.
    Replaces {#var#} in the template with  the actual OTP.
    """

    

    # Add country code if missing
    if not mobile_number.startswith("91"):
        mobile_number = f"91{mobile_number}"

    payload = {
        "Account": {
            "APIkey": settings.SMS_API_KEY,
            "SenderId": settings.SMS_SENDER_ID,
            "Channel": "2",
            "DCS": "0",
            "SchedTime": None,
            "GroupId": None,
            "EntityId": settings.SMS_ENTITY_ID,
        },
        "Messages": [
            {
                "Text": settings.SMS_OTP_TEXT.replace("{#var#}", str(otp)),
                "DLTTemplateId": settings.SMS_TEMPLATE_ID,
                "Number": mobile_number,
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            "https://www.smsgatewayhub.com/api/mt/SendSMS", 
            json=payload, 
            headers=headers,
            timeout=10
        )
        response_data = response.json()
        return response_data
    except Exception as e:
        raise




def validate_mobile(mobile):
    
    if not mobile or not mobile.isdigit():
        return False
    valid = len(mobile) == 10 or (len(mobile) == 12 and mobile.startswith("91"))
    return valid

class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile")
        
        if not validate_mobile(mobile):
            return Response({"success": False, "error": "Invalid mobile number"}, status=400)

        result = OtpService().generate_otp(
            user=None,
            otp_type=OTP_TYPE.PAN_VERIFICATION_OTP.value,
            user_mobile_number=mobile,
            lead_type=request.data.get("lead_type")
        )
        return Response({
            "success": True,
            "message": "OTP sent successfully",
            "mobile": mobile
        })

class ResendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile")

        if not validate_mobile(mobile):
            return Response({"success": False, "error": "Invalid mobile number"}, status=400)
        result = OtpService().generate_otp(
            user=None,
            otp_type=OTP_TYPE.PAN_VERIFICATION_OTP.value,
            user_mobile_number=mobile,
            lead_type=request.data.get("lead_type")
        )
        return Response({
            "success": True,
            "message": "OTP resent successfully",
            "mobile": mobile
        })

class VerifyOTPView(APIView):
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile")
        otp_entered = request.data.get("otp")

        if not validate_mobile(mobile):
            return Response({"success": False, "error": "Invalid mobile number"}, status=400)

        if not otp_entered:
            return Response({"success": False, "error": "OTP is required"}, status=400)

        try:
            userOtp = UserOtp.objects.get(Q(user__phone=mobile) | Q(user_phone_unregistered=mobile))
        except UserOtp.DoesNotExist:
            return Response({"success": False, "error": "OTP not generated for this mobile"}, status=400)
        is_valid = OtpService().verify_otp(userOtp, otp_entered)
        if not is_valid:
            return Response({"success": False, "error": "Invalid OTP"}, status=400)
        return Response({"success": True, "message": "OTP verified successfully", "mobile": mobile})
