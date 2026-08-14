import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from tele_verification.models import Videokyc
from tele_verification.serializers import VideokycSerializer
from application.models import Application
from users.models import Address
from utils.constants import ADDRESS_TYPE , APPLICANT_TYPE
from account.models import Account
import time
import hmac
import hashlib
import base64
import json
import uuid
import random

WORKAPPS_URL = "https://www.videocx.io/ims/groups/system/v1/guest/signup"

def encode_image_to_base64(file_path_or_url):
    """Convert an image file (local or URL) to a Base64 encoded string."""
    try:
        if file_path_or_url.startswith("http"):  # Check if it's a URL
            response = requests.get(file_path_or_url)
            response.raise_for_status()
            return base64.b64encode(response.content).decode("utf-8")
        else:  # Assume it's a local file path
            with open(file_path_or_url, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None
    
def generate_signature(path: str, api_secret: str) -> str:
    sha256_hmac = hmac.new(api_secret.encode('utf-8'), path.encode('utf-8'), hashlib.sha256)
    raw_hash = sha256_hmac.digest()
    signature = base64.b64encode(raw_hash).decode()
    return signature
class ForwardCustomerAPIView(APIView):
    def post(self, request):
        user=request.user
        application_id = request.GET.get("application_id")
        if not application_id:
            return Response({"error": "application_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            application = Application.objects.get(application_id=application_id)
        except Application.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
        
        house_address = Address.objects.filter(
            account=application.account, 
            address_type=ADDRESS_TYPE.CORRESPONDENCE_ADDRESS.value
        ).first()
        business_address = Address.objects.filter(
            account=application.account, 
            address_type=ADDRESS_TYPE.PERMANENT_ADDRESS.value
        ).first()
        def format_address(address):
            if address:
                return ", ".join(filter(None, [
                    address.building_name,
                    address.street_name,
                    address.city,
                    address.state,
                    address.pincode,
                    address.country
                ]))
            return None
        co_applicant = Account.objects.filter(
            applicant=application.account.user,
            applicant_type=APPLICANT_TYPE.CO_APPLICANT.value
        ).first()
        profile_photo_base64 = None
        if application.account.profile_photo:
            try:
                profile_photo_base64 = encode_image_to_base64(application.account.profile_photo.get_file_url())
            except NotImplementedError:
                print("Backend does not support absolute paths.")
            except Exception as e:
                print(f"Error reading profile photo: {e}")
        request_data = {
            # "entityId": 8814920,
            "entityId":user.entity_id,
            "productType": 4,
            "useCase": 1,
            "firstName": f"{application.account.user.first_name} {application.account.user.last_name}",
            "countryCode": "+91",
            "mobileNumber": str(application.account.user.phone).replace("+91", "", 1).strip(),
            "email": application.account.email,
            "userPhoto": profile_photo_base64,
            "data": [
                {"key": "customer_loan_number", "value": str(application.application_number)},
                {"key": "loan_amount", "value": str(application.requested_loan_amount)},
                {"key": "house_address", "value": format_address(house_address)},
                {"key": "shop_address", "value": format_address(business_address)},
                {"key": "co_applicant_name", "value": f"{co_applicant.user.first_name} {co_applicant.user.last_name}" if co_applicant else None},
                {"key": "co_applicant_email", "value": co_applicant.email if co_applicant else None},
                {"key": "co_applicant_phone_no", "value": str(co_applicant.user.phone) if co_applicant else None},
            ]
        }
        
        api_key = settings.WORKAPPS_API_KEY
        api_secret = settings.WORKAPPS_API_SECRET
        timestamp = str(int(time.time() * 1000))  # Milliseconds timestamp
        api_time_pair = f"{api_key}:{timestamp}"
        signature = generate_signature(api_time_pair, api_secret)
    
        headers = {
            "client-id": "101",
            "Content-Type": "application/json",
            "apiKey": api_key,
            "Timestamp": timestamp,
            "Signature": signature,
            "x-request-id":str(uuid.uuid4())
        }
        print("Headers:", headers)
        
        try:
            response = requests.post(WORKAPPS_URL, json=request_data, headers=headers)
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # Save to model
                    Videokyc.objects.create(
                        entity_id=user.entity_id,
                        client_user_id=random.randint(100000,999999),
                        product_type=4,
                        use_case=1,
                        first_name=f"{application.account.user.first_name} {application.account.user.last_name}",
                        customer_id=application.account.customer_id,
                        tracking_id=str(response_data.get("groupId")),  # optional mapping
                        application_id=application.application_id,
                        mobile_number=str(application.account.user.phone),
                        email=application.account.email,
                        product=application.product.product_name if application.product else None,
                        user_photo=profile_photo_base64,
                        status_url=response_data.get("redirectUrl"),
                        other_info=response_data.get("scpUrl"),
                        employee_id=user.employee_id
                    )
                
                    return Response(
                        {"message": "Customer forwarded successfully", "data": response.json()},
                        status=status.HTTP_200_OK
                    )
                except requests.exceptions.JSONDecodeError:
                    print("Error: Invalid JSON response from WorkApps API")
                    return Response(
                        {"error": "Invalid JSON response from WorkApps API", "response_text": response.text},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                return Response(
                    {"error": "Failed to forward customer", "response_text": response.text},
                    status=response.status_code
                )
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            return Response({"error": "Request to WorkApps API failed", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

WORKAPPS_CALL_LOG_URL = "https://www.videocx.io/ims/groups/system/v1/group-chat-log/"
class CallDetailsAPIView(APIView):
    def get(self, request):
        try:
            chat_instance = request.GET.get("id")
            api_key = settings.WORKAPPS_API_KEY
            api_secret = settings.WORKAPPS_API_SECRET
            timestamp = str(int(time.time() * 1000))  # Milliseconds timestamp
            api_time_pair = f"{api_key}:{timestamp}"
            signature = generate_signature(api_time_pair, api_secret)

            headers = {
                "client-id": "101",
                "Content-Type": "application/json",
                "apiKey": api_key,
                "Timestamp": timestamp,
                "Signature": signature,
                "x-request-id": "random-uuid",
            }

            response = requests.get(WORKAPPS_CALL_LOG_URL + str(chat_instance), headers=headers)

            try:
                data = response.json()
            except json.JSONDecodeError:
                return Response(
                    {
                        "error": "Invalid JSON response from WorkApps",
                        "status_code": response.status_code,
                        "response_text": response.text,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            if response.status_code == 200:
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({"error": data}, status=response.status_code)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FetchCustomerDetails(APIView):
    def get(self,request):
        try:
            application_id = request.GET.get("application_id")
            if not application_id:
                    return Response({"error": "application_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            application = Application.objects.get(application_id=application_id)
            house_address = Address.objects.filter(account=application.account, address_type=ADDRESS_TYPE.CORRESPONDENCE_ADDRESS.value).first()
            business_address = Address.objects.filter(account=application.account, address_type=ADDRESS_TYPE.PERMANENT_ADDRESS.value).first()
            def format_address(address):
                if address:
                    return ", ".join(filter(None, [
                        address.building_name,
                        address.street_name,
                        address.city,
                        address.state,
                        address.pincode,
                        address.country
                    ]))
                return None
            
            co_applicant=Account.objects.filter(
                applicant=application.account.user,
                applicant_type=APPLICANT_TYPE.CO_APPLICANT.value).first()
            response_data = {
                "customer_name": application.account.user.first_name+" "+application.account.user.last_name,
                "email": application.account.email,
                "phone_no":str( application.account.user.phone),
                "profile_pic": application.account.profile_photo.get_file_url() if application.account.profile_photo else None,
                "customer_loan_id": application.application_id,
                "loan_amount": application.requested_loan_amount,
                "house_address":format_address(house_address),
                "shop_address": format_address(business_address),
                "co_applicant_name": co_applicant.user.first_name+""+ co_applicant.user.last_name if co_applicant else None,
                "co_applicant_email":co_applicant.email if co_applicant else None,
                "co_applicant_phone_no": str(co_applicant.user.phone) if co_applicant else None
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# def encode_image_to_base64(file_path):
#     """Convert an image file to a Base64 encoded string."""
#     try:
#         with open(file_path, "rb") as image_file:
#             return base64.b64encode(image_file.read()).decode("utf-8")
#     except Exception as e:
#         return None  # Return None if file is missing or any error occurs
# def generate_signature(api_key, api_secret):
#     timestamp = str(int(time.time() * 1000))
#     api_time_pair = f"{api_key}:{timestamp}"
    
#     signature = hmac.new(
#         api_secret.encode(), api_time_pair.encode(), hashlib.sha256
#     ).digest()
    
#     return timestamp, base64.b64encode(signature).decode()
# class ForwardCustomerAPIView(APIView):
#     def post(self, request):
#         application_id = request.GET.get("application_id")
#         if not application_id:
#             return Response({"error": "application_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             application = Application.objects.get(application_id=application_id)
#         except Application.DoesNotExist:
#             return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
#         # Fetch house & business addresses
#         house_address = Address.objects.filter(
#             account=application.account, 
#             address_type=ADDRESS_TYPE.CORRESPONDENCE_ADDRESS.value
#         ).first()
#         business_address = Address.objects.filter(
#             account=application.account, 
#             address_type=ADDRESS_TYPE.PERMANENT_ADDRESS.value
#         ).first()
#         def format_address(address):
#             if address:
#                 return ", ".join(filter(None, [
#                     address.building_name,
#                     address.street_name,
#                     address.city,
#                     address.state,
#                     address.pincode,
#                     address.country
#                 ]))
#             return None
#         # Fetch co-applicant
#         co_applicant = Account.objects.filter(
#             applicant=application.account.user,
#             applicant_type=APPLICANT_TYPE.CO_APPLICANT.value
#         ).first()
#         # Fetch & encode profile photo
#         profile_photo_base64 = None
#         if application.account.profile_photo:
#             profile_photo_base64 = encode_image_to_base64(application.account.profile_photo.get_file_url())
#         # Prepare data for WorkApps API
#         request_data = {
#             "entityId": 221,
#             "productType": 4,
#             "useCase": 1,
#             "firstName": f"{application.account.user.first_name} {application.account.user.last_name}",
#             "mobileNumber": str(application.account.user.phone),
#             "email": application.account.email,
#             "userPhoto": profile_photo_base64,
#             "data": [
#                 {"key": "customer_loan_id", "value": str(application.application_id)},
#                 {"key": "loan_amount", "value": str(application.loan_amount)},
#                 {"key": "house_address", "value": format_address(house_address)},
#                 {"key": "shop_address", "value": format_address(business_address)},
#                 {"key": "co_applicant_name", "value": f"{co_applicant.user.first_name} {co_applicant.user.last_name}" if co_applicant else None},
#                 {"key": "co_applicant_email", "value": co_applicant.email if co_applicant else None},
#                 {"key": "co_applicant_phone_no", "value": str(co_applicant.user.phone) if co_applicant else None},
#             ]
#         }
#         # Generate API signature
#         api_key = settings.WORKAPPS_API_KEY
#         api_secret = settings.WORKAPPS_API_SECRET
#         print("API KEY: ",api_key)
#         print("API SECRET : ",api_secret)
#         timestamp, signature = generate_signature(api_key, api_secret)
#         headers = {
#             "client-id": "101",
#             "Content-Type": "application/json",
#             "apiKey": api_key,
#             "Timestamp": timestamp,
#             "Signature": signature,
#             # "x-request-id": "random-uuid",
#         }
#         # Make API request
#         response = requests.post(WORKAPPS_URL, json=request_data, headers=headers)
#         if response.status_code == 200:
#             return Response(
#                 {"message": "Customer forwarded successfully", "data": response.json()}, 
#                 status=status.HTTP_200_OK
#             )
#         else:
#             return Response({"error": response.json()}, status=response.status_code)
