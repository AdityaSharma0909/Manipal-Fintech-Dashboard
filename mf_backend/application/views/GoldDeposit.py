from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from utils.constants import ROLES
from application.services.application_otp import ApplicationOtpService
# from users.models import User ,UserOtp
from application.models import Application, ApplicationOtp
# from users.service.fcmService import FCMService
from utils.constants import APPLICATION_OTP_TYPE ,APPLICATION_STATUS
from users.service.fcmService import FCMService

import traceback


class GoldDepositOtpGenerator(APIView):
    def post(self, request, *agrs, **kwargs):
        try:
            application_id = request.data.get('application_id');
            if not application_id:
                return HttpResponse.BadRequest("'application_id' is required")
            
            if request.user.role == ROLES.BRANCH_MANAGER.value or request.user.role == ROLES.ASSISTANT_BRANCH_MANAGER.value:
                application=Application.objects.get(application_id=str(request.data.get('application_id')))
                # TODO: uncomment below checks
                # if application.status == APPLICATION_STATUS.GOLD_COLLECTED.value:

                otp = ApplicationOtpService().generate_otp(user=request.user, application=application, otp_type=APPLICATION_OTP_TYPE.GOLD_DEPOSIT_OTP.value)
                # TODO: Send otp to application.Originatedby.phone
                # FCMService([application.Originatedby]).generateNotification(
                #                title="Loan Deposit OTP",
                #                message=f"Your loan deposit otp for application id {application.application_number} is {otp} ",

                #            )

                return HttpResponse.Success({"otp":otp})
                # else:
                #     return HttpResponse.Forbidden("Not allowed")
            else:
                return HttpResponse.Forbidden("Not allowed")
            
        except Application.DoesNotExist as e:
            return HttpResponse.BadRequest("Invalid 'application_id' given")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    # def get(self, request, *agrs, **kwargs):
    #     try:
    #         if request.user.role == ROLES.LOAN_OFFICER.value:
    #             application=Application.objects.get(application_id=str(request.data.get('application_id')))
    #             if application.status ==APPLICATION_STATUS.LOAN_DISBURSED.value:
    #                 print("Originated by :" ,application.Originatedby)
    #                 print("otp type :",OTP_TYPE.GOLD_DEPOSIT_OTP.value)
    #                 otp_obj=UserOtp.objects.get(user=application.Originatedby,otp_type=OTP_TYPE.GOLD_DEPOSIT_OTP.value)
    #                 totp = pyotp.TOTP(otp_obj.secret_key)
    #                 otp = totp.now()
                    
    #                 return HttpResponse.Success({'otp':otp})
    #             else:
    #                 return HttpResponse.BadRequest("Loan is not disbursed")
    #         else:
    #             return HttpResponse.BadRequest("Only Loan Officer is allowed")
    #     except Exception as e:
    #         traceback.print_exc()
    #         return HttpResponse.InternalServerError(str(e))


class GoldDepositOtpVerify(APIView):
    def post(self, request, *agrs, **kwargs):
        try:
            application_id = request.data.get('application_id');
            otp = request.data.get('otp');
            if not application_id or not otp:
                return HttpResponse.BadRequest("'otp' and 'application_id' both are required")
            
            if request.user.role == ROLES.BRANCH_MANAGER.value or request.user.role == ROLES.ASSISTANT_BRANCH_MANAGER.value:
                applicationOtp = ApplicationOtp.objects.get(user=request.user, application__application_id=application_id, otp_type=APPLICATION_OTP_TYPE.GOLD_DEPOSIT_OTP.value)
                # if applicationOtp.application.status == APPLICATION_STATUS.GOLD_COLLECTED.value:

                isValidOtp = ApplicationOtpService().verify_otp(applicationOtp=applicationOtp, otp=otp)
                if isValidOtp:
                
                    applicationOtp.application.status = APPLICATION_STATUS.GOLD_DEPOSITED.value
                    applicationOtp.application.save()
                    FCMService([applicationOtp.application.Originatedby]).generateNotification(
                        title="Radian Finserv", message=f"Gold deposited for Application {applicationOtp.application.application_number}({applicationOtp.application.account.user.get_full_name()}) by {request.user.get_full_name()}."
                    )

                    return HttpResponse.Success(
                        "Gold Deposited Sucessfully"
                    )
                    # else:
                    #     return HttpResponse.BadRequest('Invalid OTP','invalid_otp')
                else:
                    return HttpResponse.Forbidden("Not allowed")
            else:
                return HttpResponse.Forbidden("Not allowed")
        except ApplicationOtp.DoesNotExist:
            return HttpResponse.BadRequest("Invalid 'application_id' given")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))