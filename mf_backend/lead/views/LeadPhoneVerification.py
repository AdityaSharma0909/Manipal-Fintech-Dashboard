from rest_framework.views import APIView
from users.serializers import CustomerGenerateOtpSerializer, VerifyOtpSerializer
from users.service.otpService import OtpService
from utils.responseHandler import HttpResponse
from rest_framework.permissions import AllowAny
from utils.constants import ROLES, OTP_TYPE
from users.models import User, UserOtp, VerificationToken

import traceback


class LeadOtpGenerationView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *agrs, **kwargs):
        try:
            phoneSer = CustomerGenerateOtpSerializer(data=request.data)
            if phoneSer.is_valid():
                otp = OtpService().generate_otp(user=None,otp_type=OTP_TYPE.LEAD_PHONE_VERIFICATION_OTP.value,user_mobile_number=request.data.get('phone'))

                return HttpResponse.Success({'otp': otp})
            else:
                return HttpResponse.BadRequest(phoneSer.errors)
        except User.DoesNotExist as e:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        

class LeadOtpVerificationView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *agrs, **kwargs):
        try:
            userSer = VerifyOtpSerializer(data=request.data)
            if userSer.is_valid():
                phone = userSer.validated_data['phone']
                userOtp = UserOtp.objects.get(user_phone_unregistered=phone)

                isValidOtp = OtpService().verify_otp(userOtp, request.data.get('otp'))
                if isValidOtp:
                    # TODO: need to pass verify token and that will be used at the time of creation
                    verificationToken = VerificationToken.objects.create(identification=phone)
                    return HttpResponse.Success({'msg':"Otp verified", 'verification_token': verificationToken.token})
                else:
                    return HttpResponse.BadRequest('Invalid OTP','invalid_otp')
            else:
                return HttpResponse.BadRequest(userSer.errors)
        except UserOtp.DoesNotExist:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))