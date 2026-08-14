from utils.envSetup import environment
from users.models import User
from application.models import Application, ApplicationOtp
from utils.sms import SMSService
from utils.constants import APPLICATION_OTP_TYPE
from utils.constants import APP_ENV

import pyotp


class ApplicationOtpService:

    def generate_otp(self, user: User, application: Application, otp_type: APPLICATION_OTP_TYPE):
        try:
            secretKey = pyotp.random_base32()
            applicationOtp, _ = ApplicationOtp.objects.update_or_create(user=user, application=application, defaults={
                'secret_key': secretKey,
                'otp_type':otp_type
            })
            totp = pyotp.TOTP(secretKey, interval=int(environment.OTP_TIMEOUT))
            otp = totp.now()
            if otp_type==APPLICATION_OTP_TYPE.GOLD_COLLECTION_OTP.value:
                mobile=application.account.user.phone
            else:
                mobile=application.Originatedby.phone
            resp=SMSService().sendGoldDepositOtp(mobile=mobile, otp=otp)
            # if environment.APP_ENV != APP_ENV.DEV.value:
            #     SMSService().sendLoginOtp(mobile=user.phone, otp=otp, name=user.first_name)
            #     return ""
            # else:
            #     return otp
            return resp
        except Exception as e:
            raise e

    def verify_otp(self, applicationOtp: ApplicationOtp, otp: str):
        try:
            totp = pyotp.TOTP(applicationOtp.secret_key, interval=int(environment.OTP_TIMEOUT))
            if totp.verify(otp):
                applicationOtp.delete()
                return True
            else:
                return False
        except Exception as e:
            raise e

