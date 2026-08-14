# from utils.responseHandler import HttpResponse
# import logging
# import traceback
# from rest_framework.views import APIView
# from rest_framework.permissions import AllowAny
# from django.contrib.auth import get_user_model
# from utils.constants import LOAN_STATUS ,OTP_TYPE
# from users.models import User, UserOtp
# from application.models import Application
# from loan.models import Loan ,LiveTracking
# from users.service.otpService import OtpService
# from account.models import Account

# from ..serializer import LiveTrackingSerializer
# User=get_user_model()

# class CollectGoldOtpView(APIView):
#     permission_classes = (AllowAny,)

#     def post(self, request, *agrs, **kwargs):
#         try:

#             application=Application.objects.get(application_id=request.data.get('application_id'))
#             account=Account.objects.get(account_id=str(application.account))
            
#             user=User.objects.get(user_id=str(account.user.user_id))

        
#             otp = OtpService().generate_otp(user,otp_type=OTP_TYPE.LOGIN_OTP.value)
#             return HttpResponse.Success({'otp': otp})
        
#         except Exception as e:
#             traceback.print_exc()
#             return HttpResponse.InternalServerError(str(e))


# class VerifyOtpView(APIView):
#     permission_classes = (AllowAny,)

#     def post(self, request, *agrs, **kwargs):
#         try:
            
#             application=Application.objects.get(application_id=request.data.get('application_id'))
#             account=Account.objects.get(account_id=str(application.account.account_id))
            
#             user=User.objects.get(user_id=str(account.user.user_id))
            
#             userOtp = UserOtp.objects.get(user=user)

#             if not userOtp:
#                 return HttpResponse.Unauthorized('Invalid credentials given')
            
#             isValidOtp = OtpService().verify_otp(userOtp, request.data.get('otp'))
#             if isValidOtp:
#                 data = OtpService().generate_token(userOtp.user)
#                 obj=Loan.objects.get(application=application)
#                 obj.status=LOAN_STATUS.ASSET_COLLECTED.value
                
#                 LiveTracking.objects.create(
#                     loan=obj,
#                     loan_manager=obj,
#                     customer=user,
#                     track_file=" From Redis track data will be moved to media storage server as csv file "
#                     ).save()
                
#                 data=LiveTracking.objects.get(loan=obj)
#                 obj.save()
                


                
#                 # TODO: delete secret key so that only one time verification is performed
#                 # and on second verification it will say already verified.
#                 # userOtp.delete()
#                 return HttpResponse.Success({
                    
#                     'Live Tracking ': LiveTrackingSerializer(data).data
#                 })
#             else:
#                 return HttpResponse.BadRequest('Invalid OTP','invalid_otp')
       
        
#         except Exception as e:
#             traceback.print_exc()
#             return HttpResponse.InternalServerError(str(e))