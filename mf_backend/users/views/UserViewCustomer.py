from django.db.models import Q
from rest_framework.views import APIView
from ..models import User, UserOtp
from ..serializers import CustomerGenerateOtpSerializer, VerifyOtpSerializer, UserModelSerializer,LoginVerifySerializer
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



class CustomerGenerateOtpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *agrs, **kwargs):
        try:
            userSer = CustomerGenerateOtpSerializer(data=request.data)
            if userSer.is_valid():
                user = User.objects.get(phone=request.data.get('phone'), is_active=True)

                # Check platform restrictions
                platform = (request.data.get('platform') or '').strip().lower()
                if not platform:
                    return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

                if platform != 'web':
                    return HttpResponse.Forbidden('Customer login is only allowed from Web')

                if (user.role != ROLES.CUSTOMER.value):
                    return HttpResponse.Unauthorized('Only customers are able to login')
                
                otp = OtpService().generate_otp(user,otp_type=OTP_TYPE.LOGIN_OTP.value)
                return HttpResponse.Success({'otp': otp})
            else:
                print("error")
                return HttpResponse.BadRequest(userSer.errors)
        except User.DoesNotExist as e:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class CustomerVerifyOtpView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *agrs, **kwargs):
        try:
            userSer = VerifyOtpSerializer(data=request.data)
            if userSer.is_valid():
                # Check platform restrictions
                platform = (request.data.get('platform') or '').strip().lower()
                if not platform:
                    return HttpResponse.BadRequest('Platform is required (web or phone)', 'missing_platform')

                if platform != 'web':
                    return HttpResponse.Forbidden('Customer login is only allowed from Web')

                userOtp = UserOtp.objects.get(
                    Q(user__phone=request.data.get('phone')) | Q(user_phone_unregistered=request.data.get('phone')))

                isValidOtp = OtpService().verify_otp(userOtp, request.data.get('otp'))
                if isValidOtp:
                    if userOtp.user is not None:
                        data = OtpService().generate_token(userOtp.user)
                        data.update(UserModelSerializer(userOtp.user).data)
                        data['account_id']=userOtp.user.account_user.all().first().account_id
                        # TODO: delete secret key so that only one time verification is performed
                        # and on second verification it will say already verified.
                        # userOtp.delete()
                        return HttpResponse.Success({
                            'user': data
                        })
                    return HttpResponse.Success({'user':"Otp verified"})
                else:
                    return HttpResponse.BadRequest('Invalid OTP','invalid_otp')
            else:
                return HttpResponse.BadRequest(userSer.errors)
        except UserOtp.DoesNotExist:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
