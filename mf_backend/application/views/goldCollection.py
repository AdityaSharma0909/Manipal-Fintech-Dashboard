from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from application.services.application_otp import ApplicationOtpService
from application.models import Application, ApplicationOtp
# from users.service.fcmService import FCMService
from utils.constants import APPLICATION_OTP_TYPE, APPLICATION_STATUS
from loan.models import LiveTracking, Loan

import traceback


class GoldCollectionOtpGenerator(APIView):
    def post(self, request, *agrs, **kwargs):
        try:                
            application_id = request.data.get('application_id');
            if not application_id:
                return HttpResponse.BadRequest("'application_id' is required")
            
            application=Application.objects.get(application_id=application_id)
            if application.status == APPLICATION_STATUS.LOAN_DISBURSED.value:

                otp = ApplicationOtpService().generate_otp(user=request.user, application=application, otp_type=APPLICATION_OTP_TYPE.GOLD_COLLECTION_OTP.value)
                # TODO: Send otp to application.Originatedby.phone
                # FCMService([application.Originatedby]).generateNotification(
                #                title="Loan Deposit OTP",
                #                message=f"Your loan deposit otp for application id {application.application_number} is {otp} ",
                #            )

                return HttpResponse.Success({"otp":otp})
            else:
                return HttpResponse.Forbidden("Not allowed")
            
        except Application.DoesNotExist as e:
            return HttpResponse.BadRequest("Invalid 'application_id' given")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))



class GoldCollectionOtpVerify(APIView):
    def post(self, request, *agrs, **kwargs):
        try:
            application_id = request.data.get('application_id');
            otp = request.data.get('otp');
            print(application_id, otp)
            if not application_id or not otp:
                return HttpResponse.BadRequest("'otp' and 'application_id' both are required")
            
            applicationOtp = ApplicationOtp.objects.get(user=request.user, application__application_id=application_id, otp_type=APPLICATION_OTP_TYPE.GOLD_COLLECTION_OTP.value)
            print('application otp',applicationOtp)
            if applicationOtp.application.status == APPLICATION_STATUS.LOAN_DISBURSED.value:
               
                isValidOtp = ApplicationOtpService().verify_otp(applicationOtp=applicationOtp, otp=otp)
                print('is valid otp',isValidOtp)
                if isValidOtp:
                   

                    loan = Loan.objects.get(application=applicationOtp.application, loan_type='GOLD_LOAN')
                    print('loans', loan)
                    liveTracking = LiveTracking.objects.create(
                        loan=loan,
                        loan_manager=applicationOtp.application.Originatedby,
                        customer=applicationOtp.application.account.user,
                        track_file="From Redis track data will be moved to media storage server as csv file."
                        )
                    print('app otp', applicationOtp.application)
                    applicationOtp.application.status = APPLICATION_STATUS.GOLD_COLLECTED.value
                    applicationOtp.application.live_tracking_id = liveTracking.track_id
                    applicationOtp.application.save()
                    print('app otp', applicationOtp.application.status)
                    return HttpResponse.Success({
                        "msg": "Gold Collected Sucessfully",
                        "track_id": liveTracking.track_id,
                    })
                else:
                    return HttpResponse.BadRequest('Invalid OTP','invalid_otp')
            else:
                return HttpResponse.Forbidden("Not allowed")
        except ApplicationOtp.DoesNotExist:
            return HttpResponse.BadRequest("Invalid 'application_id' given")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))