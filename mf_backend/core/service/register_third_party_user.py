import base64
import datetime
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from oauth2_provider.generators import generate_client_id, generate_client_secret
from oauth2_provider.models import AccessToken, RefreshToken, Application
from oauthlib import common
from account.service.accountService import AccountService

from users.models import User
from users.service.userService import UserService
from utility.common_utils import custom_response_obj
from utils.constants import ROLES


class ThirdPartyRegistrationLogin:

    def __create_apps(self, user, app_name):
        key=generate_client_id()
        secret=generate_client_secret()
        application = Application(
            name=app_name,
            client_id=key,
            client_secret=secret,
            client_type="confidential",
            authorization_grant_type="password",
            user_id=user.user_id
        )
        application.save()
        print("OAuth Application created successfully.")
        return key, secret


    def create_third_party_vendor(self, user_data):
        user_data['role']= ROLES.THIRD_PARTY_VENDOR.value
        user = UserService().register_user(user_data)
        key, secret=self.__create_apps(user, app_name=user.get_full_name()+"_"+"app")
        return custom_response_obj(message={'key':key, 'secret':secret,'user_data':user_data}, code=200)

    def authenticate_users(self, data, key_secret):
        try:
            user = User.objects.get(username=data.get('username'))
            pwd_valid = user.check_password(data.get('password'))
            print(user, pwd_valid)
            if user and pwd_valid:
                # Decode the base64 string
                decoded_bytes = base64.b64decode(key_secret)

                # Convert bytes to string
                decoded_string = decoded_bytes.decode("utf-8")

                # Split the string into key and secret
                key, secret = decoded_string.split(":", 1)
                print(key, secret)
                token=self.__generate_token(user, key, secret)
                return custom_response_obj(message=token, code=200)
            else:
                return custom_response_obj(message={'msg':"Invalid auth credentials"}, code=401)
        except ObjectDoesNotExist:
            return custom_response_obj(message={'msg':"Invalid auth credentials"}, code=401)

    def __generate_token(self,user, key, secret):
        try:
            application = Application.objects.get(client_id=key)
            expires=timezone.now() + timedelta(seconds=3600)

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
                    "expiry": 3600,
                }
        except Exception as e:
            raise e

    def register_third_party_user(self, data, created_by):
        user = UserService().createUsers({'first_name':data.get('first_name'),
                                         'last_name':data.get('last_name'),
                                         'phone':data.get('phone')}, role=ROLES.THIRD_PARTY_CUSTOMER.value)
        account=AccountService().create_account(user, data, created_by)
        return account




