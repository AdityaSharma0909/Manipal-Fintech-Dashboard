# coverfox.py
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LeegalityDocument, Invitee,User
from .serializers import LeegalityDocumentSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
import json
import base64
from django.utils import timezone
import json
from django.views import View
from django.http import JsonResponse
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from utils.constants import ROLES
from django.db import transaction
from phonenumber_field.phonenumber import PhoneNumber
import logging
import re


def _agent_phone_lookup_values(*phones):
    values = []

    def add(value):
        if value is None:
            return
        value = str(value).strip()
        if value and value not in values:
            values.append(value)

    for phone in phones:
        add(phone)
        add(getattr(phone, "as_e164", None))

        country_code = getattr(phone, "country_code", None)
        national_number = getattr(phone, "national_number", None)
        if national_number:
            add(national_number)
            if country_code:
                add(f"+{country_code}{national_number}")
                add(f"{country_code}{national_number}")

        digits = re.sub(r"\D", "", str(phone or ""))
        if not digits:
            continue

        add(digits)
        if len(digits) == 10:
            add(f"+91{digits}")
            add(f"91{digits}")
        elif digits.startswith("91") and len(digits) == 12:
            add(digits[2:])
            add(f"+{digits}")
        elif digits.startswith("0") and len(digits) == 11:
            national_digits = digits[1:]
            add(national_digits)
            add(f"+91{national_digits}")
            add(f"91{national_digits}")

    return values


def _document_invitee_phones(doc):
    phones = []
    raw_data = doc.raw_response or {}

    for invitee in raw_data.get("invitees", []):
        phone = (
            invitee.get("phone")
            or invitee.get("mobile")
            or invitee.get("contactNumber")
        )
        if phone:
            phones.append(phone)

    phones.extend(doc.invitees.values_list("phone", flat=True))
    return phones


def _find_agent_for_leegality_document(doc, lock=False):
    user_queryset = User.objects
    if lock:
        user_queryset = user_queryset.select_for_update()

    if doc.user_id:
        agent = user_queryset.filter(
            pk=doc.user_id,
            role=ROLES.AGENT.value,
        ).first()
        if agent:
            return agent

    phones = []
    if doc.agent_phone:
        phones.append(doc.agent_phone)
    phones.extend(_document_invitee_phones(doc))

    for phone in _agent_phone_lookup_values(*phones):
        agent = user_queryset.filter(
            phone=phone,
            role=ROLES.AGENT.value,
        ).first()
        if agent:
            return agent

    return None


def _generate_agent_employee_id(prefix="DSA"):
    existing_ids = User.objects.select_for_update().filter(
        role=ROLES.AGENT.value,
        employee_id__startswith=prefix,
    ).values_list("employee_id", flat=True)

    max_num = 0
    for employee_id in existing_ids:
        match = re.match(rf"^{re.escape(prefix)}(\d+)$", str(employee_id or ""))
        if match:
            max_num = max(max_num, int(match.group(1)))

    return f"{prefix}{str(max_num + 1).zfill(5)}"


def activate_agent_after_leegality_completion(doc):
    with transaction.atomic():
        locked_doc = LeegalityDocument.objects.select_for_update().get(pk=doc.pk)
        agent = _find_agent_for_leegality_document(locked_doc, lock=True)
        if not agent:
            return None, {"activated": False, "employee_id_generated": False}

        update_fields = []
        employee_id_generated = False

        if not agent.is_active:
            agent.is_active = True
            update_fields.append("is_active")

        if not agent.employee_id:
            agent.employee_id = _generate_agent_employee_id()
            update_fields.append("employee_id")
            employee_id_generated = True

        if update_fields:
            agent.save(update_fields=update_fields)

        return agent, {
            "activated": "is_active" in update_fields,
            "employee_id_generated": employee_id_generated,
        }




# class LeegalityTemplateSignRequestView(APIView):
#     """Create an eSign request for a TEMPLATE-BASED workflow in Leegality."""
#     permission_classes = [AllowAny]
#     parser_classes = [JSONParser, MultiPartParser, FormParser]  
    
    

#     def post(self, request):
#         try:
#             # Extract data
#             profile_id = request.data.get("profileId")
#             file_data = request.data.get("file", {})
#             invitees = request.data.get("invitees", [])
#             irn = request.data.get("irn", "")
#             stamp_series = request.data.get("stampSeries")
#             aadhaar_config = request.data.get("aadhaarConfig", {})

#             if not profile_id or not invitees or not stamp_series:
#                     return Response({
#                         "status": "error",
#                         "message": "profileId, invitees, and stampSeries are required",
#                         "data": None
#                     }, status=status.HTTP_400_BAD_REQUEST)

#             # Prepare payload
#             payload = {
#                 "profileId": profile_id,
#                 "file": {
#                     "name": file_data.get("name", "Template_Document"),
#                     "fields": file_data.get("fields", []),
#                 },
#                 "invitees": invitees,
#                 "stampSeries": stamp_series,
#                 "irn": irn,
#             }

#             # API credentials
#             API_URL = settings.LEEGALITY_BASE_URL
#             API_KEY = settings.LEEGALITY_AUTH_TOKEN
#             SALT_KEY = settings.LEEGALITY_SALT_KEY

#             headers = {
#                 "X-Auth-Token": API_KEY,
#                 "salt-key": SALT_KEY,
#                 "Content-Type": "application/json",
#             }

#             # Send request to Leegality
#             response = requests.post(API_URL, json=payload, headers=headers)
#             response_data = response.json()

#             # Success case
#             if response.status_code == 200 and response_data.get("status") == 1:
#                 doc_data = response_data.get("data", {})

#                 document = LeegalityDocument.objects.create(
#                     profile_id=profile_id,
#                     document_id=doc_data.get("documentId"),
#                     irn=doc_data.get("irn"),
#                 )

#                 # Save invitees
#                 for inv in doc_data.get("invitees", []):
#                     Invitee.objects.create(
#                         document=document,
#                         name=inv.get("name"),
#                         email=inv.get("email"),
#                         phone=inv.get("phone"),
#                         sign_url=inv.get("signUrl"),
#                         active=inv.get("active", True),
#                         expiry_date=inv.get("expiryDate"),
#                     )

#                 output_serializer = LeegalityDocumentSerializer(document)
#                 return Response(
#                     {
#                         "status": "success",
#                         "message": "Sign request created successfully",
#                         "data": output_serializer.data
#                     },
#                     status=status.HTTP_201_CREATED
#                 )

#             # API failure
#             return Response(
#                 {
#                     "status": "error",
#                     "message": "Failed to create sign request",
#                     "data": response_data
#                 },
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         except requests.exceptions.RequestException as e:
#             return Response(
#                 {
#                     "status": "error",
#                     "message": "Leegality API request failed",
#                     "data": str(e)
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#         except Exception as e:
#             return Response(
#                 {
#                     "status": "error",
#                     "message": "Unexpected error occurred",
#                     "data": str(e)
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#              )

class LeegalityTemplateSignRequestView(APIView):
    """Leegality eSign API - EXACT schema match."""
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        try:
            # Extract data
            profile_id = request.data.get("profileId")
            file_data = request.data.get("file", {})
            invitees = request.data.get("invitees", [])
            irn = request.data.get("irn", "")
            stamp_series = request.data.get("stampSeries")

            # Schema validation
            if not all([profile_id, invitees, stamp_series]):
                return Response({
                    "status": 0,
                    "messages": [{
                        "code": "validation.required",
                        "message": "profileId, stampSeries, and invitees are required"
                    }],
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Build payload
            payload = {
                "profileId": profile_id,
                "file": {"name": file_data.get("name", "document.pdf")},
                "invitees": invitees,
                "stampSeries": stamp_series
            }

            # File handling (PDF or Template)
            uploaded_file = request.FILES.get("pdf_file")
            if uploaded_file:
                file_size = uploaded_file.size
                if file_size > 5 * 1024 * 1024:  # 5MB limit
                    return Response({
                        "status": 0,
                        "messages": [{"code": "file.too_large", "message": f"File too large: {file_size/1024/1024:.1f}MB"}]
                    }, status=413)
                payload["file"]["file"] = base64.b64encode(uploaded_file.read()).decode()
            elif file_data.get("file"):
                payload["file"]["file"] = file_data["file"]
            elif file_data.get("fields"):
                payload["file"]["fields"] = file_data["fields"]
            else:
                return Response({
                    "status": 0,
                    "messages": [{
                        "code": "file.required", 
                        "message": "file (PDF base64/upload) or fields (template) required"
                    }],
                    "data": {}
                }, status=status.HTTP_400_BAD_REQUEST)

            if irn:
                payload["irn"] = irn

            # API call
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "salt-key": getattr(settings, 'LEEGALITY_SALT_KEY', ''),
                "Content-Type": "application/json",
            }

            response = requests.post(settings.LEEGALITY_BASE_URL, json=payload, headers=headers, timeout=60)
            response_data = response.json()

            # ✅ EXACT SCHEMA MATCH - SUCCESS
            if response.status_code == 200 and response_data.get("status") == 1:
                doc_data = response_data.get("data", {})
                
                # Save to DB
                create_kwargs = {
                    "profile_id": profile_id,
                    "document_id": doc_data.get("documentId"),
                    "irn": doc_data.get("irn", irn),
                }
                if getattr(request, "user", None) is not None and getattr(request.user, "is_authenticated", False):
                    create_kwargs["user"] = request.user
                document = LeegalityDocument.objects.create(**create_kwargs)
                print(f"DEBUG: Document created ID={document.id}")
                agent_phone = request.data.get("agent_phone")
                if agent_phone:
                    LeegalityDocument.objects.filter(id=document.id).update(agent_phone=agent_phone) 

                for inv in doc_data.get("invitees", []):
                    Invitee.objects.create(
                        document=document,
                        name=inv.get("name"),
                        email=inv.get("email"),
                        phone=inv.get("phone"),
                        sign_url=inv.get("signUrl"),
                        active=inv.get("active", True),
                        expiry_date=inv.get("expiryDate"),
                    )

                return Response({
                    "status": 1,
                    "messages": [],
                    "data": {
                        "documentId": doc_data.get("documentId"),
                        "irn": doc_data.get("irn", irn),
                        "invitees": doc_data.get("invitees", [])
                    }
                }, status=status.HTTP_201_CREATED)

            # ✅ EXACT SCHEMA MATCH - ERROR  
            return Response({
                "status": 0,
                "messages": response_data.get("messages", [{
                    "code": "leegality.error",
                    "message": "Failed to create eSign request"
                }]),
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "status": 0,
                "messages": [{
                    "code": "network.error",
                    "message": "Leegality API unavailable"
                }],
                "data": {}
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as db_error:
            print(f"DB ERROR: {db_error}")
            return Response({
                "status": 0,
                "messages": [{
                    "code": "server.error", 
                    "message": "Internal server error"
                }],
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class LeegalityTransactionStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            document_id = request.query_params.get("documentId")
            if not document_id:
                return Response(
                    {"error": "documentId is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            api_url = settings.LEEGALITY_BASE_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "salt-key": settings.LEEGALITY_SALT_KEY,
                "Content-Type": "application/json",
            }

            params = {"documentId": document_id}
            response = requests.get(api_url, headers=headers, params=params)
            response_data = response.json()

            # Leegality success
            if response.status_code == 200 and response_data.get("status") == 1:
                data = response_data.get("data", {})
                requests_data = data.get("requests", [])

                # Extract signed status for all invitees
                signed_statuses = [req.get("signed", False) for req in requests_data]

                # Determine Verification Result
                agent_activation = None

                if requests_data and all(signed_statuses):
                    verification_status = "Verified successfully"
                elif any(signed_statuses):
                    verification_status = "Partially signed"
                else:
                    verification_status = "Not signed yet"

                # Persist status to DB if document exists
                try:
                    doc = LeegalityDocument.objects.get(document_id=document_id)
                    if verification_status == "Verified successfully":
                        doc.status = LeegalityDocument.STATUS_COMPLETED
                        doc.is_verified = True
                    elif verification_status == "Partially signed":
                        doc.status = LeegalityDocument.STATUS_PENDING
                        doc.is_verified = False
                    else:
                        doc.status = LeegalityDocument.STATUS_PENDING
                        doc.is_verified = False
                    # Store the latest raw response for audit/debug
                    doc.raw_response = data
                    doc.save(update_fields=["status", "is_verified", "raw_response", "updated_at"])
                    if verification_status == "Verified successfully":
                        agent, activation = activate_agent_after_leegality_completion(doc)
                        if agent:
                            agent_activation = {
                                **activation,
                                "employee_id": agent.employee_id,
                                "agent_phone": str(agent.phone),
                            }
                except LeegalityDocument.DoesNotExist:
                    pass

                return Response(
                    {
                        "message": "Transaction fetched successfully",
                        "verification_status": verification_status,
                        "total_invitees": len(requests_data),
                        "signed_count": signed_statuses.count(True),
                        "pending_count": signed_statuses.count(False),
                        "agent_activation": agent_activation,
                        "data": data,
                    },
                    status=status.HTTP_200_OK,
                )

            # API Failed
            return Response(
                {
                    "error": "Failed to fetch transaction status",
                    "api_response": response_data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "Leegality API request failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as e:
            return Response(
                {"error": "Unexpected error occurred", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )





class LeegalityUserEsignStatusView(APIView):
    permission_classes = []

    def get(self, request):
        user_id = getattr(request.user, "user_id", None)

        if not user_id:
            return Response({
                "status": 0,
                "messages": [{
                    "code": "validation.required",
                    "message": "authenticated user required"
                }],
                "data": {}
            }, status=status.HTTP_401_UNAUTHORIZED)

        doc = None

        doc = LeegalityDocument.objects.filter(user_id=user_id).order_by("-updated_at").first()

        if not doc:
            return Response({
                "status": 1,
                "messages": [],
                "data": {
                    "completed": False,
                    "documentId": None,
                    "status": LeegalityDocument.STATUS_PENDING,
                    "verified": False,
                    "updatedAt": None
                }
            }, status=status.HTTP_200_OK)

        completed = bool(doc.is_verified or doc.status == LeegalityDocument.STATUS_COMPLETED)

        return Response({
            "status": 1,
            "messages": [],
            "data": {
                "completed": completed,
                "documentId": doc.document_id,
                "status": doc.status,
                "verified": doc.is_verified,
                "updatedAt": doc.updated_at
            }
        }, status=status.HTTP_200_OK)

class LeegalityDeleteDocumentView(APIView):
    """
    Delete a document in Leegality using POST request with documentId
    """
    permission_classes = [AllowAny]

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            document_id = request.data.get("documentId")

            if not document_id:
                return Response(
                    {"error": "documentId is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            api_url = settings.LEEGALITY_DOCUMENT_DELETE_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "salt-key": settings.LEEGALITY_SALT_KEY,
                "Content-Type": "application/json",
            }

            payload = {"documentId": document_id}

            response = requests.post(api_url, json=payload, headers=headers)

            try:
                response_data = response.json()
            except ValueError:
                response_data = {"status": response.status_code, "messages": [{"message": "No JSON content returned"}]}

           

            #  Success
            if response.status_code == 200 and response_data.get("status") == 1:
                LeegalityDocument.objects.filter(document_id=document_id).delete()
                return Response({
                    "message": f"Document {document_id} deleted successfully",
                    "api_response": response_data
                }, status=status.HTTP_200_OK)

            # ❌ Failure
            return Response({
                "error": "Failed to delete document",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeegalitySearchDocumentsView(APIView):
    """
    Search existing documents in Leegality using query params
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # ✅ Get query params from request
            search_query = request.query_params.get("q", "")
            status_filter = request.query_params.get("status", "")
            max_records = request.query_params.get("max", 20)
            offset = request.query_params.get("offset", 0)

            # ✅ Validate query
            if not search_query and not status_filter:
                return Response(
                    {"error": "Please provide either 'q' or 'status' as a query parameter."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Prepare API call
            api_url = settings.LEEGALITY_SEARCH_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "salt-key": settings.LEEGALITY_SALT_KEY,
                "Content-Type": "application/json",
            }

            params = {
                "q": search_query,
                "status": status_filter,
                "max": max_records,
                "offset": offset,
            }

            # ✅ Make GET request
            response = requests.get(api_url, headers=headers, params=params)
            response_data = response.json()

         

            # ✅ Success case
            if response.status_code == 200 and response_data.get("status") == 1:
                return Response({
                    "message": "Documents fetched successfully",
                    "data": response_data.get("data", {})
                }, status=status.HTTP_200_OK)

            # ❌ Failure case
            return Response({
                "error": "Failed to fetch documents",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeegalityReactivateDocumentView(APIView):
    """
    Reactivate expired documents within 30 days using Leegality API
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # ✅ Get the input data
            document_id = request.data.get("documentId")
            expiry_days = request.data.get("expiryDays", 10)
            expiry_time = request.data.get("expiryTime", 0)

            # ✅ Validate input
            if not document_id:
                return Response(
                    {"error": "documentId is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Prepare the payload
            payload = {
                "documentId": document_id,
                "expiryDays": expiry_days,
                "expiryTime": expiry_time
            }

            # ✅ Headers for the request
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "salt-key": settings.LEEGALITY_SALT_KEY,
                "Content-Type": "application/json",
            }

            # ✅ Send the POST request
            api_url = settings.LEEGALITY_REACTIVATE_URL
            response = requests.post(api_url, headers=headers, json=payload)
            response_data = response.json()

            

            # ✅ Check for success
            if response.status_code == 200 and response_data.get("status") == 1:
                return Response({
                    "message": "Document reactivated successfully",
                    "data": response_data.get("data", {})
                }, status=status.HTTP_200_OK)

            # ❌ Failure case
            return Response({
                "error": "Failed to reactivate document",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeegalityResendNotificationView(APIView):
    """
    Resend notifications for given sign URLs.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            sign_urls = request.data.get("signUrls", [])

            # ✅ Validation
            if not sign_urls or not isinstance(sign_urls, list):
                return Response(
                    {"error": "signUrls must be a list and cannot be empty"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            api_url = settings.LEEGALITY_RESEND_NOTIFICATION_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "Content-Type": "application/json",
            }

            payload = {"signUrls": sign_urls}

            response = requests.post(api_url, json=payload, headers=headers)
            response_data = response.json()

            

            # ✅ Success case
            if response.status_code == 200 and response_data.get("status") == 1:
                return Response({
                    "message": "Notifications resent successfully",
                    "data": response_data.get("data", {})
                }, status=status.HTTP_200_OK)

            # ❌ Failure case
            return Response({
                "error": "Failed to resend notifications",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LeegalityDeleteInvitationView(APIView):
    """
    Delete an unsigned invitation from a document using its signUrl.
    """
    permission_classes = [AllowAny]

    def delete(self, request):
        try:
            sign_url = request.query_params.get("signUrl")

            # ✅ Validate input
            if not sign_url:
                return Response(
                    {"error": "signUrl is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            api_url = settings.LEEGALITY_DELETE_INVITATION_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "Content-Type": "application/json",
            }

            params = {"signUrl": sign_url}

            # ✅ Send DELETE request
            response = requests.delete(api_url, headers=headers, params=params)

            # Some DELETE APIs may return no content (status 204)
            if response.status_code == 204:
                return Response({
                    "message": "Invitation deleted successfully (no content returned)"
                }, status=status.HTTP_200_OK)

            # Otherwise, try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"status": response.status_code, "messages": [{"message": "No JSON content returned"}]}

            

            # ✅ Success case
            if response.status_code == 200 and response_data.get("status") == 1:
                return Response({
                    "message": "Invitation deleted successfully",
                    "data": response_data
                }, status=status.HTTP_200_OK)

            # ❌ Failure case
            return Response({
                "error": "Failed to delete invitation",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeegalityMarkDocumentCompleteView(APIView):
    """
    Mark an incomplete Leegality document as completed.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            document_id = request.data.get("documentId")

            # ✅ Validation
            if not document_id:
                return Response(
                    {"error": "documentId is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            api_url = settings.LEEGALITY_MARK_COMPLETE_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "Content-Type": "application/json",
            }

            payload = {"documentId": document_id}

            # ✅ Send POST request
            response = requests.post(api_url, headers=headers, json=payload)

            # Try to parse JSON
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"status": response.status_code, "messages": [{"message": "No JSON content returned"}]}

            

            # ✅ Success case
            if response.status_code == 200 and response_data.get("status") == 1:
                try:
                    doc = LeegalityDocument.objects.get(document_id=document_id)
                    doc.status = LeegalityDocument.STATUS_COMPLETED
                    doc.is_verified = True
                    doc.raw_response = response_data
                    doc.save(update_fields=["status", "is_verified", "raw_response", "updated_at"])
                    activate_agent_after_leegality_completion(doc)
                except LeegalityDocument.DoesNotExist:
                    pass

                return Response({
                    "message": "Document marked as complete successfully",
                    "data": response_data
                }, status=status.HTTP_200_OK)

            # ❌ Failure case
            return Response({
                "error": "Failed to mark document as complete",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeegalityDocumentDetailsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            document_id = request.query_params.get("documentId")
            if not document_id:
                return Response(
                    {"error": "documentId is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            api_url = settings.LEEGALITY_DOCUMENT_DETAILS_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "Content-Type": "application/json",
            }

            params = {
                "documentId": document_id,
                "file": False,
                "auditTrail": False,
                "attachments": False,
                "failureReason": False,
                "verificationResponse": False,
            }

         

            response = requests.get(api_url, headers=headers, params=params)
            

            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == 1:
                return Response({
                    "message": "Document details fetched successfully",
                    "data": response_data.get("data", {})
                }, status=status.HTTP_200_OK)

            return Response({
                "error": "Failed to fetch document details",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeegalityCompletedDocumentsView(APIView):
    """
    Fetch list of completed documents from Leegality.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # 1️⃣ Extract query params
            max_records = request.query_params.get("max", 20)
            offset = request.query_params.get("offset", 0)
            name = request.query_params.get("name", "")
            irn = request.query_params.get("irn", "")
            start_date = request.query_params.get("startDate", "")
            end_date = request.query_params.get("endDate", "")

            # 2️⃣ Prepare headers
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "Content-Type": "application/json"
            }

            # 3️⃣ Prepare query params
            params = {
                "max": max_records,
                "offset": offset,
                "name": name,
                "irn": irn,
                "startDate": start_date,
                "endDate": end_date
            }

            # Remove empty params
            params = {k: v for k, v in params.items() if v}

            # 4️⃣ API URL from settings
            api_url = settings.LEEGALITY_COMPLETED_DOCUMENTS_URL

            

            # 5️⃣ Make GET request
            response = requests.get(api_url, headers=headers, params=params)
            response_data = response.json()

            

            # 6️⃣ Success
            if response.status_code == 200 and response_data.get("status") == 1:
                return Response({
                    "message": "Completed documents fetched successfully",
                    "data": response_data.get("data", {})
                }, status=status.HTTP_200_OK)

            # ❌ Failure
            return Response({
                "error": "Failed to fetch completed documents",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeegalityDocSignerSignView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            sign_url = request.data.get("signUrl")
            profile_id = request.data.get("profileId")

            if not sign_url or not profile_id:
                return Response({
                    "error": "signUrl and profileId are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            payload = {
                "signUrl": sign_url,
                "profileId": profile_id,
                "consent": (
                    "By using this authenticated API and the ProfileID associated with this "
                    "Document Signer Certificate, I agree that the Document Signer Certificate "
                    "saved in this Account will be used to eSign documents for me. I also understand "
                    "that recipients of such electronic documents will be able to see my signing details."
                )
            }

            api_url = settings.LEEGALITY_DOCSIGNER_INVITATION_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "Content-Type": "application/json",
            }

            response = requests.post(api_url, json=payload, headers=headers)
            response_data = response.json()

            

            if response.status_code == 200 and response_data.get("status") == 1:
                return Response({
                    "message": "Document eSigned successfully",
                    "data": response_data.get("data", {})
                }, status=status.HTTP_200_OK)

            return Response({
                "error": "Failed to eSign document",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    
class LeegalityStampDetailsView(APIView):
    """
    Fetch all stamp series details from Leegality
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            api_url = settings.LEEGALITY_STAMP_DETAILS_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "Content-Type": "application/json",
            }

            # Call the Leegality Stamp Details API
            response = requests.get(api_url, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == 1:
                return Response({
                    "message": "Stamp details fetched successfully",
                    "data": response_data.get("data", {})
                }, status=status.HTTP_200_OK)

            # Failure case
            return Response({
                "error": "Failed to fetch stamp details",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LeegalityStampGroupsView(APIView):
    """
    Fetch all stamp groups details from Leegality
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            api_url = settings.LEEGALITY_STAMP_GROUPS_URL
            headers = {
                "X-Auth-Token": settings.LEEGALITY_AUTH_TOKEN,
                "Content-Type": "application/json",
            }

            # Call the Leegality Stamp Groups API
            response = requests.get(api_url, headers=headers)
            response_data = response.json()

            if response.status_code == 200 and response_data.get("status") == 1:
                return Response({
                    "message": "Stamp groups fetched successfully",
                    "data": response_data.get("data", {})
                }, status=status.HTTP_200_OK)

            # Failure case
            return Response({
                "error": "Failed to fetch stamp groups",
                "api_response": response_data
            }, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.RequestException as e:
            return Response({
                "error": "Leegality API request failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
   
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny

# from users.models import User
# from .models import LeegalityDocument
# from utils.constants import ROLES

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction

import json

class LeegalityWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            logging.getLogger(__name__).info("Leegality webhook hit")
            data = request.data
            document_id = data.get("documentId")
            sign_status = data.get("status")

            if not document_id:
                return Response({
                    "status": 0,
                    "messages": [{
                        "code": "validation.required",
                        "message": "documentId missing"
                    }],
                    "data": {}
                }, status=400)

            doc = LeegalityDocument.objects.select_related("user").get(
                document_id=document_id
            )

            # ✅ Store JSON-safe webhook payload
            doc.raw_response = json.loads(json.dumps(data))

            # ===============================
            # ✅ COMPLETED
            # ===============================
            if sign_status == "COMPLETED":
                with transaction.atomic():

                    doc.status = LeegalityDocument.STATUS_COMPLETED
                    doc.is_verified = True
                    doc.save(update_fields=["status", "is_verified", "raw_response"])

                    agent, activation = activate_agent_after_leegality_completion(doc)

                    # ❌ Agent not found
                    if not agent:
                        return Response({
                            "status": 1,
                            "messages": [{
                                "code": "esign.completed.no_agent",
                                "message": "eSign completed but agent not found"
                            }],
                            "data": {
                                "documentId": document_id,
                                "status": "COMPLETED"
                            }
                        }, status=200)

                    # ✅ CASE 1: Already verified
                    if not activation["activated"] and not activation["employee_id_generated"]:
                        return Response({
                            "status": 1,
                            "messages": [{
                                "code": "esign.already.completed",
                                "message": "You already completed eSign verification"
                            }],
                            "data": {
                                "documentId": document_id,
                                "employee_id": agent.employee_id,
                                "agent_phone": str(agent.phone),
                                "agent_name": f"{agent.first_name or ''} {agent.last_name or ''}".strip(),
                                "status": "COMPLETED"
                            }
                        }, status=200)

                    return Response({
                        "status": 1,
                        "messages": [{
                            "code": "esign.completed",
                            "message": "eSign completed successfully. Agent activated."
                        }],
                        "data": {
                            "documentId": document_id,
                            "employee_id": agent.employee_id,
                            "agent_phone": str(agent.phone),
                            "agent_name": f"{agent.first_name or ''} {agent.last_name or ''}".strip(),
                            "status": "COMPLETED"
                        }
                    }, status=200)

            # ===============================
            # ❌ FAILED
            # ===============================
            if sign_status == "FAILED":
                doc.status = LeegalityDocument.STATUS_FAILED
                doc.save(update_fields=["status", "raw_response"])

                return Response({
                    "status": 1,
                    "messages": [{
                        "code": "esign.failed",
                        "message": "eSign verification failed"
                    }],
                    "data": {
                        "documentId": document_id,
                        "status": "FAILED"
                    }
                }, status=200)

            # ===============================
            # ℹ️ OTHER STATUSES
            # ===============================
            return Response({
                "status": 1,
                "messages": [{
                    "code": "status.updated",
                    "message": "Document status updated"
                }],
                "data": {
                    "documentId": document_id,
                    "status": sign_status
                }
            }, status=200)

        except LeegalityDocument.DoesNotExist:
            return Response({
                "status": 0,
                "messages": [{
                    "code": "document.not_found",
                    "message": "Document not found"
                }],
                "data": {}
            }, status=404)

        except Exception as e:
            return Response({
                "status": 0,
                "messages": [{
                    "code": "server.error",
                    "message": str(e)
                }],
                "data": {}
            }, status=500)

    # ===================================================
    # Helpers
    # ===================================================

    def _find_agent_safely(self, doc):
        return _find_agent_for_leegality_document(doc)

    def generate_employee_id(self):
        """
        Generates DSA00001, DSA00002 safely.
        """
        return _generate_agent_employee_id()
