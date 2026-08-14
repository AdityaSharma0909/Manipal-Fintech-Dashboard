from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import OpenApiExample, extend_schema
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import UserOtp, VerificationToken
from ..serializers import (
    ForgotPasswordRequestSerializer,
    ForgotPasswordVerifySerializer,
    ForgotPasswordResetSerializer,
)
from ..service.otpService import OtpService
from utils.responseHandler import HttpResponse
from utils.constants import OTP_TYPE
from utils.helper import sendForgotPasswordEmail
import traceback
from utils.envSetup import environment

User = get_user_model()

class ForgotPasswordRequestView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Request forgot password OTP",
        description="Sends an OTP to the user's registered phone number for password reset.",
        request=ForgotPasswordRequestSerializer,
        examples=[
            OpenApiExample(
                name="Forgot Password Request Payload",
                value={
                    "phone": "7001385745",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            serializer = ForgotPasswordRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            phone = serializer.validated_data['phone']

            try:
                user = User.objects.get(phone=phone, is_active=True)
            except User.DoesNotExist:
                return HttpResponse.NotFound("User with this phone number does not exist.")

            # if not user.email:
            #     return HttpResponse.BadRequest("User does not have a registered email address.")

            # Generate OTP
            otp = OtpService().generate_otp(user, otp_type=OTP_TYPE.FORGOT_PASSWORD_OTP.value)

            # Send OTP to email (optional, keeping it for double channel)
            # sendForgotPasswordEmail(
            #     email=user.email,
            #     otp=otp,
            #     name=f"{user.first_name} {user.last_name}"
            # )

            resp = {"message": "OTP sent to your registered phone number and email."}
            try:
                if (getattr(environment, "APP_ENV", "") or "").upper() != "PROD" and getattr(environment, "MASTER_OTP", None):
                    resp['master_otp'] = environment.MASTER_OTP
            except Exception:
                pass
            return HttpResponse.Success(resp)

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class ForgotPasswordVerifyView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Verify forgot password OTP",
        description="Verifies the OTP and returns a verification token for password reset.",
        request=ForgotPasswordVerifySerializer,
        examples=[
            OpenApiExample(
                name="Forgot Password Verify Payload",
                value={
                    "phone": "7001385745",
                    "otp": "727272",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            serializer = ForgotPasswordVerifySerializer(data=request.data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            phone = serializer.validated_data['phone']
            otp = serializer.validated_data['otp']

            try:
                user_otp = UserOtp.objects.get(
                    user__phone=phone,
                    otp_type=OTP_TYPE.FORGOT_PASSWORD_OTP.value
                )
            except UserOtp.DoesNotExist:
                return HttpResponse.Unauthorized("Invalid request or OTP expired.")

            is_valid = OtpService().verify_otp(user_otp, otp)
            if is_valid:
                # Generate verification token for resetting password
                verification_token = VerificationToken.objects.create(
                    identification=str(phone)
                )
                return HttpResponse.Success({
                    "message": "OTP verified successfully.",
                    "verification_token": verification_token.token
                })
            else:
                return HttpResponse.BadRequest("Invalid OTP.")

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class ForgotPasswordResetView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Reset password with verification token",
        description="Resets the user's password using the verification token returned after OTP verification.",
        request=ForgotPasswordResetSerializer,
        examples=[
            OpenApiExample(
                name="Forgot Password Reset Payload",
                value={
                    "verification_token": "d1f782a8-ec11-481b-bc71-2b7967f19e62",
                    "new_password": "Manipal@123",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        try:
            serializer = ForgotPasswordResetSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            token = serializer.validated_data['verification_token']
            new_password = serializer.validated_data['new_password']

            try:
                vt = VerificationToken.objects.get(token=token)
                if vt.expiry < timezone.now():
                    vt.delete()
                    return HttpResponse.Unauthorized("Verification token expired.")
            except VerificationToken.DoesNotExist:
                return HttpResponse.Unauthorized("Invalid verification token.")

            try:
                user = User.objects.get(phone=vt.identification, is_active=True)
                user.set_password(new_password)
                user.save()
                
                # Delete the verification token after successful reset
                vt.delete()
                
                return HttpResponse.Success({"message": "Password reset successfully."})
            except User.DoesNotExist:
                return HttpResponse.NotFound("User not found.")

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class ForgotPasswordUpdateView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            username = request.data.get('username')
            new_password = request.data.get('new_password')

            if not username or not new_password:
                return HttpResponse.BadRequest("Username and new password are required.")

            username = str(username).strip()

            from django.db.models import Q
            import re
            
            try:
                # Make username and employee_id case-insensitive
                q = Q(username__iexact=username) | Q(employee_id__iexact=username)
                
                # Only check against the phone field if the username doesn't contain letters
                if re.match(r'^\+?[0-9\-\s]+$', username):
                    q |= Q(phone=username)
                    
                user = User.objects.get(q)
                
                if not user.is_active:
                    return HttpResponse.BadRequest("User account is inactive. Please contact admin.")

            except User.DoesNotExist:
                return HttpResponse.NotFound("User not found.")
            except User.MultipleObjectsReturned:
                return HttpResponse.BadRequest("Multiple users found with these details.")

            user.set_password(new_password)
            user.save()

            return HttpResponse.Success({"message": "Password updated successfully."})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class RememberMeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            from ..serializers import RememberMeSerializer
            serializer = RememberMeSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            from django.db.models import Q
            import re

            try:
                # Search using the same versatile logic we built for ForgotPassword
                q = Q(username__iexact=username) | Q(employee_id__iexact=username)
                if re.match(r'^\+?[0-9\-\s]+$', username):
                    q |= Q(phone=username)
                
                user = User.objects.get(q)
            except User.DoesNotExist:
                return HttpResponse.NotFound("User not found.")
            except User.MultipleObjectsReturned:
                return HttpResponse.BadRequest("Multiple users matching this identifier.")

            user.remember_username = username
            user.remember_password = password
            user.save()

            return HttpResponse.Success({"message": "Remember Me credentials saved successfully."})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
