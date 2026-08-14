from users.models import User, UserDeviceDetails
from pyfcm import FCMNotification
from django.conf import settings
from typing import List
import traceback


class FCMService:
    def __init__(self, users: List[User]):
        try:
            self.user_details = UserDeviceDetails.objects.filter(user__in=users)
            self.pushTokens = [u.push_token for u in self.user_details]
        except UserDeviceDetails.DoesNotExist as e:
            traceback.print_exc()
        except Exception as e:
            traceback.print_exc()

    def generateNotification(self, title: str, message: str):
        try:
            self.push_service = FCMNotification(api_key=settings.FCM_API_KEY)
            if len(self.pushTokens) > 0:
                result = self.push_service.notify_multiple_devices(
                    registration_ids=self.pushTokens,
                    message_title=title,
                    message_body=message,
                )
                print("Sending notification: ", result)
        except Exception as e:
            traceback.print_exc()

