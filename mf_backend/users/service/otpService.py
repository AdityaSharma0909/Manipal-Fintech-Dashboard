from users.models import User, UserOtp, UserDeviceDetails
from datetime import timedelta

from django.utils import timezone
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauth2_provider.settings import oauth2_settings
from oauthlib import common
from django.conf import settings
from utils.responseHandler import HttpResponse
from utils.constants import APP_ENV, ROLES, OTP_TYPE
import pyotp
from django.contrib.auth.hashers import check_password
from utils.envSetup import environment
from utils.sms import SMSService


class OtpService:

    def generate_otp(self, user, otp_type, user_mobile_number=None, lead_type=None):
        try:
            secretKey = pyotp.random_base32()
            if user is not None:
                UserOtp.objects.filter(user_phone_unregistered=user.phone).delete()
                userOtp, _ = UserOtp.objects.update_or_create(user=user, defaults={
                    'secret_key': secretKey,
                    'otp_type': otp_type
                })
                phone = user.phone
                name = user.first_name
            else:
                userOtp, _ = UserOtp.objects.update_or_create(user_phone_unregistered=user_mobile_number, defaults={
                    'secret_key': secretKey,
                    'otp_type': otp_type
                })
                phone = user_mobile_number
                name = None

            # phone = user.phone
            # name = user.first_name

            totp = pyotp.TOTP(secretKey, interval=int(environment.OTP_TIMEOUT))
            otp = totp.now()
            #if environment.APP_ENV != APP_ENV.DEV.value:
            return self.__send_otp(mobile=phone, otp=otp, name=name, otp_type=otp_type, lead_type=lead_type)
                #SMSService().sendLoginOtp(mobile=user.phone, otp=otp, name=user.first_name)
            #     return ""
            # else:
            #return otp
        except Exception as e:
            raise e

    def __send_otp(self,mobile, otp, name,otp_type='login', lead_type=None):
        sms_service=SMSService()

        if otp_type==OTP_TYPE.LOGIN_OTP.value:
            return sms_service.sendLoginOtp(mobile=mobile, otp=otp)

        if otp_type==OTP_TYPE.ACCOUNT_PHONE_VERIFICATION_OTP.value:
            return sms_service.verify_mobile_number(mobile=mobile, otp=otp)

        if otp_type==OTP_TYPE.LEAD_PHONE_VERIFICATION_OTP.value:
            return sms_service.sendLeadGenerationOtp(mobile=mobile, otp=otp)

        if otp_type==OTP_TYPE.PAN_VERIFICATION_OTP.value:
            return sms_service.sendPanVerificationOtp(mobile=mobile, otp=otp, lead_type=lead_type)

        if otp_type==OTP_TYPE.GOLD_COLLECT_VERIFICATION.value or otp_type==OTP_TYPE.GOLD_DEPOSIT_VERIFICATION.value:
            return sms_service.sendGoldDepositOtp(mobile, otp)

        if otp_type==OTP_TYPE.FORGOT_PASSWORD_OTP.value:
            # Send SMS with custom DLT template
            return sms_service.sendForgotPasswordOtp(mobile=mobile, otp=otp)



    def verify_otp(self, userOtp: UserOtp, otp):
        try:
            # Master OTP for non-production testing
            try:
                if getattr(environment, "MASTER_OTP", None) and str(otp) == str(environment.MASTER_OTP):
                    userOtp.delete()
                    return True
            except Exception:
                pass
            totp = pyotp.TOTP(userOtp.secret_key, interval=int(environment.OTP_TIMEOUT))
            if totp.verify(otp):
                userOtp.delete()
                return True
            else:
                return False
        except Exception as e:
            raise e

    def generate_token(self, user):
        try:
            if user.role==ROLES.LOAN_OFFICER.value:
                AccessToken.objects.filter(user__username=user.username).delete()
                RefreshToken.objects.filter(user__username=user.username).delete()
                UserDeviceDetails.objects.filter(user__username=user.username).delete()
            application, _ = Application.objects.get_or_create(
                name="Radian App",
                defaults={
                    "client_type": Application.CLIENT_CONFIDENTIAL,
                    "authorization_grant_type": Application.GRANT_PASSWORD,
                    "redirect_uris": "",
                },
            )

            # For test users
            if (environment.TEST_LM_PHONE == user.phone and user.username == environment.TEST_LM_USERNAME) or user.phone == environment.TEST_CUSTOMER_PHONE:
                expire_days = 365 * 10
            else:
                expire_days = settings.ACCESS_TOKEN_EXPIRY_IN_DAYS
            expires = timezone.now() + timedelta(
                days=expire_days
            )
            current_token = common.generate_token()
            refresh_token = common.generate_token()

            access_token = AccessToken(
                user=user,
                scope="",
                expires=expires,
                token=current_token,
                application=application,
            )
            access_token.save()
            refresh_token_data = RefreshToken(
                user=user,
                token=refresh_token,
                application=application,
                access_token=access_token,
            )
            refresh_token_data.save()
            return {
                "access_token": current_token,
                "refresh_token": refresh_token,
                "expiry": expires,
            }
        except Exception as e:
            raise e


class LoginService:
    def authenticate(self, username=None, password=None):
        login_valid = User.objects.get(username=username).username == username
        pwd_valid = check_password(
            password, User.objects.get(username=username).password
        )
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return HttpResponse.Unauthorized({"error": "User does not exist"})
            return user
        return None
