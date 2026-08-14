from rest_framework import authentication
from rest_framework import exceptions

from utils.constants import ROLES
from utils.envSetup import environment
from django.contrib.auth.models import AnonymousUser
from rest_framework import status as drfStatus
import requests

authHeader = 'HTTP_X_QUANTUM_ARC_KEY';

class ServerUser(AnonymousUser):
    
    def __init__(
            self,
            user_id,
            last_login,
            kite_user_id,
            api_key,
            access_token,
            request_token,
            user_type,
            email,
            user_name,
            created_at,
            modified_at,
            role=None,

            **kwargs
        ) -> None:
        super().__init__()
        self.user_id = user_id
        self.last_login = last_login
        self.kite_user_id = kite_user_id
        self.api_key=api_key
        self.access_token = access_token
        self.request_token = request_token
        self.user_type = user_type
        self.email = email
        self.user_name = user_name
        self.created_at = created_at
        self.modified_at = modified_at
        self.role = role
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def is_authenticated(self):
        # Always return True. This is a way to tell if
        # the user has been authenticated in permissions
        return True


class CustomAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request, **kwargs):
        token = request.META.get(authHeader)
        if not token:
            return None
        try:
            status_code, user = self.getUser(token)
            role = user.get('role') if isinstance(user, dict) else getattr(user, 'role', None)
            print(role)
            if (role==ROLES.BUSINESS_HEAD.value or role==ROLES.CHIEF_BUSINESS_OPERATOR.value) and request.method!='GET':
                raise exceptions.PermissionDenied('You do not have edit access')
            # TODO: check if othet status code than 200 goes in exeception or not
            if status_code == drfStatus.HTTP_403_FORBIDDEN:
                return None
            elif status_code != drfStatus.HTTP_200_OK:
                return None
        except Exception as e:
            print(str(e))
            raise exceptions.AuthenticationFailed('Invalid auth credentials')

        u = ServerUser(**user)
        return (u, None)

    def getUser(self, token):
        url = environment.AUTH_SERVICE_BASEURL + "/user"
        headers = {
            'x-quantum-arc-key': token
        }
        response = requests.request("GET", url, headers=headers)
        return response.status_code, response.json()


from rest_framework.permissions import BasePermission

class CustomPermission(BasePermission):
    """
    Custom permission class example.
    """

    def has_permission(self, request, view):
        """
        Override this method to define custom permission logic.

        Return True if the request should be granted access,
        and False otherwise.
        """

        role = request.user.role
        if (role == ROLES.BUSINESS_HEAD.value or role == ROLES.CHIEF_BUSINESS_OPERATOR.value) and request.method != 'GET':
            return False
        return request.user

    def has_object_permission(self, request, view, obj):
        """
        Override this method to define custom object-level permission logic.

        Return True if the request should be granted access to the given object,
        and False otherwise.
        """
        # Example: Check if the user owns the object
        role = request.user.role
        if (role == ROLES.BUSINESS_HEAD.value or role == ROLES.CHIEF_BUSINESS_OPERATOR.value) and request.method != 'GET':
            return False
        return request.user


from rest_framework.permissions import BasePermission

class ThirdPartyPermission(BasePermission):
    """
    Custom permission class example.
    """

    def has_permission(self, request, view):
        """
        Override this method to define custom permission logic.

        Return True if the request should be granted access,
        and False otherwise.
        """
        user=request.user
        print(user.__str__())
        if user.__str__() != 'AnonymousUser':
            role = user.role
            if role==ROLES.THIRD_PARTY_VENDOR.value or role==ROLES.SUPER_ADMIN.value or role==ROLES.VERTICAL_ADMIN.value or role==ROLES.CPC.value:
                return request.user
            return False
        return False

    def has_object_permission(self, request, view, obj):
        """
        Override this method to define custom object-level permission logic.

        Return True if the request should be granted access to the given object,
        and False otherwise.
        """
        # Example: Check if the user owns the object

        user = request.user
        if user!='AnonymousUser':
            role = user.role
            if role == ROLES.THIRD_PARTY_VENDOR.value or role == ROLES.SUPER_ADMIN.value or role == ROLES.VERTICAL_ADMIN.value or role == ROLES.CPC.value:
                return request.user
            return False
        return False