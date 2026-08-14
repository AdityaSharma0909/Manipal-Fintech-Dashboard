from rest_framework.views import APIView

from users.models import UserDeviceDetails
from users.serializers import UserDeviceDetailsModelSerializer
from utils.responseHandler import HttpResponse
# from rest_framework.permissions import AllowAny
import logging

import traceback
from utils.constants import ACCOUNT_STATUS

log = logging.getLogger("radian")


class UserDeviceView(APIView):

    def post(self, request):
        data = request.data
        user = request.user
        try:

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ipaddress = x_forwarded_for.split(',')[-1].strip()
            else:
                ipaddress = request.META.get('REMOTE_ADDR')

            data["user"] = user.user_id
            data["ip_address"] = ipaddress
            serializer = UserDeviceDetailsModelSerializer(data=data)
            if serializer.is_valid():
                obj, created = UserDeviceDetails.objects.update_or_create(
                    user=request.user,
                    platform_type=request.data.get("platform_type", "web"),
                    device_id=serializer.validated_data['device_id'],
                    defaults=serializer.validated_data,
                )
                # serializer.save()

                return HttpResponse.Success(serializer.data)
            else:
                log.error(
                    "[{user} | POST | UserDeviceView Error] Error - {error}".format(
                        user=user, error=serializer.errors
                    )
                )
                return HttpResponse.BadRequest(serializer.errors)
        except Exception as e:
            traceback.print_exc()
            log.error(
                "[{user} | POST | UserDeviceView Exception] Exception - {error}".format(
                    user=user, error=e
                )
            )
            return HttpResponse.InternalServerError(str(e))

    # def get(self, request):
    #     user = request.user
    #     try:
    #         user_details_id = request.GET.get("user_details_id")
    #         if user_details_id:
    #             user_device = UserDeviceDetails.objects.get(
    #                 user_details_id=user_details_id
    #             )
    #             serializer = UserDeviceDetailsModelSerializer(user_device)
    #         else:
    #             user_devices = UserDeviceDetails.objects.all()
    #             serializer = UserDeviceDetailsModelSerializer(user_devices, many=True)

    #         # serializer=UserDeviceDetailsModelSerializer(user_devices,many=True)
    #         return HttpResponse.Success(serializer.data)

    #     except UserDeviceDetails.DoesNotExist as e:
    #         log.error(
    #             "[{user} | GET | UserDeviceView Error] Error - {error}".format(
    #                 user=user, error=e
    #             )
    #         )
    #         return HttpResponse.BadRequest(str(e))
    #         # return HttpResponse.BadRequest({"errors": e})
    #     except Exception as e:
    #         log.error(
    #             "[{user} | GET | UserDeviceView Exception] Exception - {error}".format(
    #                 user=user, error=e
    #             )
    #         )
    #         traceback.print_exc()
    #         return HttpResponse.InternalServerError(str(e))
    #         # return HttpResponse.InternalServerError({"errors": e})

    # def patch(self, request):
    #     data = request.data
    #     user = request.user
    #     try:
    #         user_details_id = request.GET.get("user_details_id")
    #         if not user_details_id:
    #             return HttpResponse.BadRequest("'user_details_id' is required!")

    #         user_device = UserDeviceDetails.objects.get(user_details_id=user_details_id)
    #         serializer = UserDeviceDetailsModelSerializer(
    #             user_device, data=data, partial=True
    #         )
    #         if serializer.is_valid():
    #             serializer.save()
    #             return HttpResponse.Success(serializer.data)

    #         log.error(
    #             "[{user} | PATCH | UserDeviceView Error] Error - {error}".format(
    #                 user=user, error=e
    #             )
    #         )
    #         return HttpResponse.BadRequest(serializer.errors)
    #     except UserDeviceDetails.DoesNotExist as e:
    #         log.error(
    #             "[{user} | PATCH | UserDeviceView Error] Error - {error}".format(
    #                 user=user, error=e
    #             )
    #         )
    #         return HttpResponse.BadRequest(e)
    #     except Exception as e:
    #         traceback.print_exc()
    #         log.error(
    #             "[{user} | PATCH | UserDeviceView Exception] Exception - {error}".format(
    #                 user=user, error=e
    #             )
    #         )
    #         return HttpResponse.InternalServerError(str(e))
    #         # return HttpResponse.InternalServerError(e)

    # def delete(self, request):
    #     user = request.user
    #     try:
    #         user_details_id = request.GET.get("user_details_id")
    #         if not user_details_id:
    #             return HttpResponse.BadRequest("'user_details_id' is required!")

    #         user_device = UserDeviceDetails.objects.get(user_details_id=user_details_id)
    #         serializer = UserDeviceDetailsModelSerializer(user_device)
    #         user_device.delete()

    #         return HttpResponse.Success(serializer.data)
    #     except UserDeviceDetails.DoesNotExist as e:
    #         log.error(
    #             "[{user} | DELETE | UserDeviceView Error] Error - {error}".format(
    #                 user=user, error=e
    #             )
    #         )
    #         return HttpResponse.BadRequest(str(e))
    #     except Exception as e:
    #         traceback.print_exc()
    #         log.error(
    #             "[{user} | DELETE | UserDeviceView Exception] Exception - {error}".format(
    #                 user=user, error=e
    #             )
    #         )
    #         return HttpResponse.InternalServerError(str(e))


# class FCMNotificationView(APIView):
#     def get(self, request):
#         user = self.user
#         data = self.data
#         try:
#             title = request.data.get("title")
#             message = request.data.get("message")
#             if not title or not message:
#                 return HttpResponse.BadRequest("'title' and 'message' are required!")

#             service = FCMService(user)
#             success, data = service.generateNotification()
#             if not success:
#                 return HttpResponse.BadRequest(data)

#             return HttpResponse.Success(data)
#         except UserDeviceDetails.DoesNotExist as e:
#             return HttpResponse.BadRequest(str(e))
#             # return HttpResponse.BadRequest({"errors": e})
#         except Exception as e:
#             traceback.print_exc()
#             return HttpResponse.InternalServerError(str(e))


# black ./users/views/FCMView.py
