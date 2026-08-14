# from users.models import User, UserDeviceDetails
from pyfcm import FCMNotification


push_service: FCMNotification = FCMNotification(
    api_key="AAAA1B6MIG4:APA91bGiXhcE4vF6FNJJkblTrS9f7wqxDciiWF6SGIbIGW2pIFrnXnuHRot8F2bzdHMwfU0gwBVPQ1jjbzgsNjIQ9_chIzHj0T8nx74tQL64DgJ1VaL7Kq1NsuwiY-VtBAX_kNlVmm6Y"
)

# # OR initialize with proxies

# proxy_dict = {
#           "http"  : "http://127.0.0.1",
#           "https" : "http://127.0.0.1",
#         }
# push_service = FCMNotification(api_key="radian-finserv", proxy_dict=proxy_dict)

# # Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging

registration_id = "eZzA9sQvRTOgB5NgjQL71-:APA91bHQbw0UGS0eAthpz9J4Bq831xbS2NmoLACPRq0eblOHSy-WrTja045b45cL6RIwrGYlSYvK2YgkS54SMLoMHrWiptllZGcI98J4yhaDdzr0wM_zB7D82GLL7Jn4YYJRgpeezxDW"
message_title = "Uberrrrrrrrrr update"
message_body = "Hi john, your customized news for today is ready"
result = push_service.notify_single_device(
    registration_id=registration_id,
    message_title=message_title,
    message_body=message_body,
)

# Send to multiple devices by passing a list of ids.
# registration_ids = ["<device registration_id 1>", "<device registration_id 2>", ...]
# message_title = "Uber update"
# message_body = "Hope you're having fun this weekend, don't forget to check today's news"
# result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)

