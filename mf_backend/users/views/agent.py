import re

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
from utils.envSetup import environment
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse


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


def _get_user_by_agent_phone(*phones):
    for phone in _agent_phone_lookup_values(*phones):
        try:
            return User.objects.get(phone=phone)
        except User.DoesNotExist:
            continue
    return None


def _get_agent_otp_by_phone(phone, raw_phone=None, user=None):
    if user is not None:
        try:
            return UserOtp.objects.get(user=user)
        except UserOtp.DoesNotExist:
            pass

    for lookup_phone in _agent_phone_lookup_values(phone, raw_phone):
        try:
            return UserOtp.objects.get(
                Q(user__phone=lookup_phone) | Q(user_phone_unregistered=lookup_phone)
            )
        except UserOtp.DoesNotExist:
            continue

    raise UserOtp.DoesNotExist


class AgentGenerateOtpView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Generate OTP for Agent Login",
        request=AgentGenerateOtpSerializer,
        responses={
            200: OpenApiResponse(
                description="OTP generated successfully.",
                examples=[
                    OpenApiExample(
                        "OTP Generated Successfully",
                        value={
                            "status": "success",
                            "message": {
                                "otp": "123456",
                                "user_exists": True
                            }
                        },
                        response_only=True,
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Bad request.",
                examples=[
                    OpenApiExample(
                        "Bad Request",
                        value={
                            "status": "error",
                            "message": "Platform is required (web or phone)"
                        },
                        response_only=True,
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Unauthorized.",
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "status": "error",
                            "message": "Invalid credentials given"
                        },
                        response_only=True,
                    ),
                ],
            ),
            403: OpenApiResponse(
                description="Forbidden.",
                examples=[
                    OpenApiExample(
                        "Forbidden",
                        value={
                            "status": "error",
                            "message": "Agent login is only allowed from Phone"
                        },
                        response_only=True,
                    ),
                ],
            ),
            500: OpenApiResponse(
                description="Internal server error.",
                examples=[
                    OpenApiExample(
                        "Internal Server Error",
                        value={
                            "status": "error",
                            "message": "Internal server error occurred"
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def post(self, request, *agrs, **kwargs):
        try:
            userSer = AgentGenerateOtpSerializer(data=request.data)
            if userSer.is_valid():
                raw_phone = request.data.get('phone')
                phone = userSer.validated_data['phone']
                user = _get_user_by_agent_phone(phone, raw_phone)
                user_exists = user is not None

                # Check platform restrictions
                platform = (request.data.get('platform') or '').strip().lower()
                if not platform:
                    return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

                if platform != 'phone':
                    return HttpResponse.Forbidden('Agent login is only allowed from Phone')

                if user and user.role != ROLES.AGENT.value:
                    return HttpResponse.Unauthorized('Only agents are allowed to login')
                
                otp = OtpService().generate_otp(
                    user,
                    otp_type=OTP_TYPE.LOGIN_OTP.value,
                    user_mobile_number=str(phone),
                )
                resp = {
                    'otp': otp,
                    'user_exists': user_exists
                }
                # try:
                #     if (getattr(environment, "APP_ENV", "") or "").upper() != "PROD" and getattr(environment, "MASTER_OTP", None):
                #         resp['master_otp'] = environment.MASTER_OTP
                # except Exception:
                #     pass
                return HttpResponse.Success(resp)
            else:
                print("error")
                return HttpResponse.BadRequest(userSer.errors)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class AgentVerifyOtpView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Verify OTP for Agent Login",
        request=VerifyOtpSerializer,
        responses={
            200: OpenApiResponse(
                description="OTP verified successfully.",
                examples=[
                    OpenApiExample(
                        "OTP Verified Successfully (Existing User)",
                        value={
                            "status": "success",
                            "message": {
                                "user": {
                                    "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                                    "phone": "+917001586476",
                                    "employee_id": "DSA00001",
                                    "access_token": "...",
                                    "refresh_token": "...",
                                    "expiry": "..."
                                },
                                "user_exists": True
                            }
                        },
                        response_only=True,
                    ),
                    OpenApiExample(
                        "OTP Verified Successfully (New User Created)",
                        value={
                            "status": "success",
                            "message": {
                                "user": {
                                    "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                                    "phone": "+919999999999",
                                    "employee_id": "DSA00002",
                                    "access_token": "...",
                                    "refresh_token": "...",
                                    "expiry": "..."
                                },
                                "user_exists": False
                            }
                        },
                        response_only=True,
                    ),
                ],
            ),
            400: OpenApiResponse(
                description="Bad request.",
                examples=[
                    OpenApiExample(
                        "Bad Request",
                        value={
                            "status": "error",
                            "message": "Invalid OTP"
                        },
                        response_only=True,
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Unauthorized.",
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "status": "error",
                            "message": "Invalid credentials given"
                        },
                        response_only=True,
                    ),
                ],
            ),
            403: OpenApiResponse(
                description="Forbidden.",
                examples=[
                    OpenApiExample(
                        "Forbidden",
                        value={
                            "status": "error",
                            "message": "Agent login is only allowed from Phone"
                        },
                        response_only=True,
                    ),
                ],
            ),
            500: OpenApiResponse(
                description="Internal server error.",
                examples=[
                    OpenApiExample(
                        "Internal Server Error",
                        value={
                            "status": "error",
                            "message": "Internal server error occurred"
                        },
                        response_only=True,
                    ),
                ],
            ),
        },
    )
    def post(self, request, *agrs, **kwargs):
        try:
            userSer = VerifyOtpSerializer(data=request.data)
            if userSer.is_valid():
                # Check platform restrictions
                platform = (request.data.get('platform') or '').strip().lower()
                if not platform:
                    return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

                if platform != 'phone':
                    return HttpResponse.Forbidden('Agent login is only allowed from Phone')

                raw_phone = request.data.get('phone')
                phone = userSer.validated_data['phone']
                user = _get_user_by_agent_phone(phone, raw_phone)

                if user and user.role != ROLES.AGENT.value:
                    return HttpResponse.Unauthorized('Only agents are allowed to login')

                # TODO: need to add new constants in otp for account phone verification
                userOtp = _get_agent_otp_by_phone(phone, raw_phone=raw_phone, user=user)

                isValidOtp = OtpService().verify_otp(userOtp, request.data.get('otp'))
                if isValidOtp:
                    if userOtp.user is not None:
                        user = userOtp.user

                        data = OtpService().generate_token(user)
                        data.update(UserModelSerializer(user).data)
                        data.pop('employee_id', None)
                        return HttpResponse.Success({
                            'user': data,
                            'user_exists': True
                        })
                    else:
                        phone_value = getattr(phone, "as_e164", None) or str(phone)
                        # Create user if not exists
                        user = User.objects.create_user(
                            username=phone_value,
                            phone=phone_value,
                            role=ROLES.AGENT.value,
                            is_active=False,
                            employee_id=None
                        )
                        print("New inactive agent user created during OTP verification")
                        user_exists = False

                        data = OtpService().generate_token(user)
                        data.update(UserModelSerializer(user).data)
                        data.pop('employee_id', None)
                        return HttpResponse.Success({
                            'user': data,
                            'user_exists': user_exists
                        })
                else:
                    return HttpResponse.BadRequest('Invalid OTP','invalid_otp')
            else:
                return HttpResponse.BadRequest(userSer.errors)
        except UserOtp.DoesNotExist:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class AgentView(APIView):

    def get(self, request):
        try:
            user_id = request.GET.get("user_id", "")
            if not user_id:
                return HttpResponse.BadRequest("User id is required!")

            user = User.objects.get(user_id=user_id)
            serializer = UserModelSerializer(user)
            return HttpResponse.Success({"user": serializer.data})
        except User.DoesNotExist:
            return HttpResponse.BadRequest("User not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def patch(self, request):
        try:
            data = request.data
            user_id = request.GET.get("user_id", "")
            user = User.objects.get(user_id=user_id)

            # Step 1: Get employee_id from request data
            assign_so_employee_id = data.get("assign_so") or data.get("assign_so_id")

            if assign_so_employee_id:
                # Step 2: Find the User object matching this employee_id
                try:
                    assign_so_user = User.objects.get(employee_id=assign_so_employee_id)
                    # Step 3: Replace employee_id in data with user_id (UUID)
                    data["assign_so"] = str(assign_so_user.user_id)
                except User.DoesNotExist:
                    return HttpResponse.BadRequest(
                        {"error": f"No user found with employee_id {assign_so_employee_id}"}
                    )

            # Step 4: Serialize and update the User record
            serializer = UserModelSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()

                # Step 5: Build enriched response (add assign_so details)
                response_data = serializer.data
                if user.assign_so:
                    response_data["assign_so"] = {
                        "user_id": str(user.assign_so.user_id),
                        "employee_id": user.assign_so.employee_id,
                        "full_name": f"{user.assign_so.first_name or ''} {user.assign_so.last_name or ''}".strip(),
                        "city": user.assign_so.city,
                    }

                return HttpResponse.Success({"user": response_data})

            return HttpResponse.BadRequest(serializer.errors)

        except User.DoesNotExist:
            return HttpResponse.BadRequest({"error": "User record not found."})

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
