import traceback
from django.core.mail import EmailMessage
from utils.envSetup import environment


class PasswordService:

    def reset_password_email(self,token, subject, email):
        try:
            msg = EmailMessage(subject=subject,
                               from_email=f"Password reset <{environment.DEFAULT_FROM_EMAIL}>",
                               body=f"Please click the link below to reset http://uat-app.radianfinserv.com/#/resetPassword/{token}",
                               to=[email])

            msg.send()
        except Exception:
            traceback.print_exc()

