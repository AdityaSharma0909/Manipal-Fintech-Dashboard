from django.db.models import Q
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
from rest_framework.views import APIView
from rest_framework import serializers
from ..models import User, UserOtp, VerificationToken
from ..serializers import GenerateOtpSerializer, VerifyOtpSerializer, UserModelSerializer,LoginVerifySerializer
from ..service.otpService import OtpService,LoginService
from utils.responseHandler import HttpResponse
import logging
import traceback
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from utils.constants import ROLES ,OTP_TYPE
from django.contrib.auth.password_validation import validate_password

User=get_user_model()

log = logging.getLogger('users')

# class AppBaseAPIView(APIView):

#     def post(self, request, *agrs, **kwargs):
#         try:
#             return Response({
#                 'status': 'success',
#                 "error": str(e)
#             }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({
#                 'status': 'error',
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


class GenerateOtpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *agrs, **kwargs):
        try:
            userSer = GenerateOtpSerializer(data=request.data)
            if userSer.is_valid():
                try:
                    user = User.objects.get(phone=request.data.get('phone'), username__exact=request.data.get('username'))
                except User.DoesNotExist:
                    return HttpResponse.Unauthorized('Invalid credentials given')

                if not user.is_active:
                    return HttpResponse.Unauthorized('Your account has been put on hold. Please contact Admin for this.')

                # Check platform restrictions
                platform = (request.data.get('platform') or '').strip().lower()
                if not platform:
                    return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

                if platform == 'web':
                    if user.role in [ROLES.SALES_OFFICER.value, ROLES.AGENT.value]:
                        return HttpResponse.Forbidden('Sales Officers and Agents are not allowed to generate OTP from Web')
                elif platform == 'phone':
                    if user.role not in [ROLES.SALES_OFFICER.value, ROLES.AGENT.value]:
                        return HttpResponse.Forbidden('Only Sales Officers and Agents are allowed to generate OTP from Phone')
                else:
                    return HttpResponse.BadRequest('Invalid platform. Must be web or phone.', 'invalid_platform')

                if user.role != ROLES.CPC.value:
                    return HttpResponse.Unauthorized('Invalid credentials given')

                if (user.role != ROLES.LOAN_OFFICER.value and user.role!=ROLES.ASSISTANT_BRANCH_MANAGER.value and user.role!=ROLES.BRANCH_MANAGER.value and user.role!=ROLES.RELATIONSHIP_MANAGER.value and user.role!=ROLES.CREDIT_OFFICER.value):
                    return HttpResponse.Unauthorized('loan manager and Relationship manager are only allowed to login')
                if not user:
                    return HttpResponse.Unauthorized('Invalid credentials given')

                otp = OtpService().generate_otp(user,otp_type=OTP_TYPE.LOGIN_OTP.value)
                return HttpResponse.Success({'otp': otp})
            else:
                print("error")
                return HttpResponse.BadRequest(userSer.errors)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class VerifyOtpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *agrs, **kwargs):
        try:
            userSer = VerifyOtpSerializer(data=request.data)
            if userSer.is_valid():
                phone = userSer.validated_data['phone']

                # Check platform restrictions
                platform = (request.data.get('platform') or '').strip().lower()
                if not platform:
                    return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

                try:
                    user = User.objects.get(phone=phone)
                except User.DoesNotExist:
                    return HttpResponse.Unauthorized('Invalid credentials given')

                if platform == 'web':
                    if user.role in [ROLES.SALES_OFFICER.value, ROLES.AGENT.value]:
                        return HttpResponse.Forbidden('Sales Officers and Agents are not allowed to verify OTP from Web')
                elif platform == 'phone':
                    if user.role not in [ROLES.SALES_OFFICER.value, ROLES.AGENT.value]:
                        return HttpResponse.Forbidden('Only Sales Officers and Agents are allowed to verify OTP from Phone')
                else:
                    return HttpResponse.BadRequest('Invalid platform. Must be web or phone.', 'invalid_platform')

                userOtp = UserOtp.objects.get(
                    Q(user__phone=phone) | Q(user_phone_unregistered=phone))

                isValidOtp = OtpService().verify_otp(userOtp, request.data.get('otp'))
                if isValidOtp:
                    if userOtp.user is not None:
                        data = OtpService().generate_token(userOtp.user)
                        data.update(UserModelSerializer(userOtp.user).data)
                        # TODO: delete secret key so that only one time verification is performed
                        # and on second verification it will say already verified.
                        # userOtp.delete()
                        return HttpResponse.Success({
                            'user': data
                        })
                    else:

                        verificationToken = VerificationToken.objects.create(identification=phone)
                        return HttpResponse.Success({'user':"Otp verified", 'verification_token': verificationToken.token})
                else:
                    return HttpResponse.BadRequest('Invalid OTP','invalid_otp')
            else:
                return HttpResponse.BadRequest(userSer.errors)
        except UserOtp.DoesNotExist:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
class LoginView(APIView):
    permission_classes = (AllowAny,)
    @extend_schema(
        summary="User login",
        request=LoginVerifySerializer,
        examples=[
            OpenApiExample(
                "Sales Officer Login",
                value={
                    "username": "SG009",
                    "password": "Manipal@123",
                    "platform": "phone"
                },
                request_only=True,
            ),
            OpenApiExample(
                "CPC User Login",
                value={
                    "username": "cpc123",
                    "password": "Radian@123",
                    "platform": "web"
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *agrs, **kwargs):
        try:
            identifier = (request.data.get('username') or '').strip()
            if not identifier:
                return HttpResponse.BadRequest('Username or phone is required', 'missing_username')

            # Try to fetch user by phone or username, regardless of is_active
            user = None
            try:
                user = User.objects.get(phone=identifier)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username__exact=identifier)
                except User.DoesNotExist:
                    return HttpResponse.Unauthorized('Invalid credentials given')

            if not user.is_active:
                return HttpResponse.Unauthorized('Your account has been put on hold. Please contact Admin for this.')

            # Check platform restrictions
            platform = (request.data.get('platform') or '').strip().lower()
            if not platform:
                return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

            if platform == 'web':
                if user.role in [ROLES.SALES_OFFICER.value, ROLES.AGENT.value]:
                    return HttpResponse.Forbidden('Sales Officers and Agents are not allowed to login from Web')
            elif platform == 'phone':
                if user.role not in [ROLES.SALES_OFFICER.value, ROLES.AGENT.value, ROLES.REGIONAL_HEAD.value]:
                    return HttpResponse.Forbidden('Only Sales Officers, Agents, and Regional Heads are allowed to login from Phone')
            else:
                return HttpResponse.BadRequest('Invalid platform. Must be web or phone.', 'invalid_platform')

            userSer = LoginVerifySerializer(data=request.data)
            if userSer.is_valid():
                isValidLogin = LoginService().authenticate(username=user.username, password=request.data.get('password', ''))
                if isValidLogin:
                    data = OtpService().generate_token(isValidLogin)
                    data.update(UserModelSerializer(isValidLogin).data)
                    return HttpResponse.Success({
                        'user': data
                    })
                else:
                    return HttpResponse.BadRequest('Invalid User', 'invalid_user')
            else:
                return HttpResponse.BadRequest(userSer.errors)
        except UserOtp.DoesNotExist:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class SalesOfficerLoginView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=["Users"],
        operation_id="sales_officer_login",
        summary="Sales officer login",
        description="Authenticate a sales officer using username or phone and password.",
        request=LoginVerifySerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="SalesOfficerLoginSuccessResponse",
                    fields={
                        "status": serializers.CharField(default="success"),
                        "data": inline_serializer(
                            name="SalesOfficerLoginSuccessData",
                            fields={
                                "user": serializers.DictField(),
                            },
                        ),
                    },
                ),
                description="Sales officer authenticated successfully.",
            ),
            400: OpenApiResponse(description="Invalid login payload."),
            401: OpenApiResponse(description="Invalid credentials."),
        },
        examples=[
            OpenApiExample(
                name="Sales Officer Login Payload",
                value={
                    "username": "SG009",
                    "password": "Manipal@123",
                    "platform": "phone"
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *agrs, **kwargs):
        try:
            identifier = (request.data.get('username') or '').strip()
            if not identifier:
                return HttpResponse.BadRequest('Username or phone is required', 'missing_username')

            # User model uses USERNAME_FIELD = "phone"; accept phone or username in "username" field
            try:
                user = User.objects.get(phone=identifier, is_active=True)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username__exact=identifier, is_active=True)
                except User.DoesNotExist:
                    return HttpResponse.Unauthorized('Invalid credentials given')

            if user.role != ROLES.SALES_OFFICER.value:
                return HttpResponse.Unauthorized('Invalid credentials given')

            # Check platform restrictions
            platform = (request.data.get('platform') or '').strip().lower()
            if not platform:
                return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

            if platform != 'phone':
                return HttpResponse.Forbidden('Sales Officer login is only allowed from Phone')

            userSer = LoginVerifySerializer(data=request.data)
            if userSer.is_valid():
                isValidLogin = LoginService().authenticate(username=user.username, password=request.data.get('password', ''))
                
                if isValidLogin:
                    data = OtpService().generate_token(isValidLogin)
                    data.update(UserModelSerializer(isValidLogin).data)
                    return HttpResponse.Success({
                        'user': data
                    })
                else:
                    return HttpResponse.BadRequest('Invalid User', 'invalid_user')
            else:
                return HttpResponse.BadRequest(userSer.errors)
        except UserOtp.DoesNotExist:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class PasswordChangeView(APIView):
    def patch(self, request, *agrs, **kwargs):
        user = request.user
        try:
            data = request.data
            # fetched_user = User.objects.get(user_id = user.user_id)
            fetched_user: User = user
            old_password = data["old_password"]
            
            if fetched_user.check_password(old_password):
                new_password = data["new_password"]
                
                if old_password == new_password:
                    return HttpResponse.BadRequest("New password should not be the same as the old one")
                
                validate_password(new_password, fetched_user)
                fetched_user.set_password(new_password)
                fetched_user.save()
                
            else:
                print("Yo!")
                return HttpResponse.BadRequest("Incorrect 'old_password'")
            
            user = UserModelSerializer(fetched_user)
            return HttpResponse.Success({
                'user': user.data
            })
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class UserByIdView(APIView):
    def get(self, request):
        try:
            user_ids = request.data.get("user_id", "")

            if not user_ids:
                return HttpResponse.BadRequest("user_id is required")

            # Support comma-separated or list input
            if isinstance(user_ids, str):
                user_ids = [uid.strip() for uid in user_ids.split(",") if uid.strip()]

            users = User.objects.filter(user_id__in=user_ids)

            if not users.exists():
                return HttpResponse.NotFound("No users found for given IDs")

            user_info = [
                {
                    "user_id": str(u.user_id),
                    "employee_id": u.employee_id,
                    "full_name": f"{u.first_name or ''} {u.last_name or ''}".strip()
                }
                for u in users
            ]

            return HttpResponse.Success({
                "total_users": users.count(),
                "users": user_info
            })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
