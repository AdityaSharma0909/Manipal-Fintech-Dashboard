from django.db.models import Q
from rest_framework.views import APIView
from ..models import User, UserOtp, VerificationToken
from ..serializers import GenerateOtpSerializer, VerifyOtpSerializer, UserModelSerializer,AgentGenerateOtpSerializer
from ..service.otpService import OtpService
from utils.responseHandler import HttpResponse
import logging
import traceback
from rest_framework.permissions import AllowAny
from utils.constants import ROLES ,OTP_TYPE
from django.contrib.auth.password_validation import validate_password


class SalesOfficerGenerateOtpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *agrs, **kwargs):
        try:
            userSer = AgentGenerateOtpSerializer(data=request.data)
            if userSer.is_valid():
                try:
                    user = User.objects.get(phone=request.data.get('phone'), is_active=True)
                except User.DoesNotExist:
                    print("User does not exist")
                
                # Check platform restrictions
                platform = (request.data.get('platform') or '').strip().lower()
                if not platform:
                    return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

                if platform != 'phone':
                    return HttpResponse.Forbidden('Sales Officer login is only allowed from Phone')

                otp = OtpService().generate_otp(user,otp_type=OTP_TYPE.LOGIN_OTP.value)
                return HttpResponse.Success({'otp': otp})
            else:
                print("error")
                return HttpResponse.BadRequest(userSer.errors)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
class SalesOfficerVerifyOtpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            phone = data.get("phone")
            otp = data.get("otp")

            # Check platform restrictions
            platform = (data.get('platform') or '').strip().lower()
            if not platform:
                return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

            if platform != 'phone':
                return HttpResponse.Forbidden('Sales Officer login is only allowed from Phone')

            if not phone or not otp:
                return HttpResponse.BadRequest("Phone and OTP are required")

            # Step 1: Get OTP entry
            try:
                userOtp = UserOtp.objects.get(
                    Q(user__phone=phone) | Q(user_phone_unregistered=phone)
                )
            except UserOtp.DoesNotExist:
                return HttpResponse.BadRequest("OTP not found or expired")

            # Step 2: Verify OTP
            isValidOtp = OtpService().verify_otp(userOtp, otp)
            if not isValidOtp:
                return HttpResponse.BadRequest("Invalid OTP", "invalid_otp")

            # Step 3: Create temporary verification token
            verificationToken = VerificationToken.objects.create(identification=phone)

            return HttpResponse.Success({
                "message": "OTP verified successfully",
                "verification_token": verificationToken.token
            })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
class SalesOfficerSetNewPasswordView(APIView):
    permission_classes = (AllowAny,)

    def patch(self, request, *args, **kwargs):
        try:
            data = request.data
            verification_token = data.get("verification_token")
            new_password = data.get("new_password")
            confirm_password = data.get("confirm_password")

            if not all([verification_token, new_password, confirm_password]):
                return HttpResponse.BadRequest("verification_token, new_password and confirm_password are required")

            if new_password != confirm_password:
                return HttpResponse.BadRequest("New password and confirm password do not match")

            # Step 1: Verify token is valid
            try:
                verifyToken = VerificationToken.objects.get(token=verification_token)
            except VerificationToken.DoesNotExist:
                return HttpResponse.BadRequest("Invalid or expired verification token")

            phone = verifyToken.identification

            # Step 2: Get user by phone
            try:
                user = User.objects.get(phone=phone, is_active=True)
            except User.DoesNotExist:
                return HttpResponse.Unauthorized("User not found")

            # Step 3: Validate password & update
            validate_password(new_password, user)
            user.set_password(new_password)
            user.save()

            # Step 4: Invalidate token so it can't be reused
            verifyToken.delete()

            user_data = UserModelSerializer(user).data
            return HttpResponse.Success({
                "message": "Password changed successfully",
                "user": user_data
            })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
