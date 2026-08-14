import logging

from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from insurance.coverfox.insurance_services import get_sso_url
from insurance.coverfox.serializers import CoverFoxSerializer

logger = logging.getLogger(__name__)

def get_serializer_error(serializer):
    return next(iter(serializer.errors.values()), ["Invalid request."])[0]

def build_response(success, message, data=None, status_code=status.HTTP_200_OK):
        return Response(
            {
                "success": success,
                "message": message,
                "data": data,
            },
            status=status_code)

HTTP_ERROR_MESSAGES = {
        400: "Missing or invalid request fields.",
        401: "Unauthorized access.",
        403: "Client is not whitelisted for this environment.",
        404: "SSO URL not found.",
        429: "Rate limit exceeded. Please try again later.",
        500: "Internal server error.",
}

class CoverFoxView(APIView):
    permission_classes = []

    @extend_schema(request=CoverFoxSerializer)
    def post(self, request):
        serializer = CoverFoxSerializer(data=request.data)
        if not serializer.is_valid():
            return build_response(
                False,
                get_serializer_error(serializer),
                status_code=status.HTTP_400_BAD_REQUEST)

        try:
            data = serializer.validated_data
            request_payload = {
                "name": data["name"],
                "mobile": data["mobile"],
                "email": data["email"],
                "customer_id": request.user.employee_id
            }
            print("coverfox request_payload:----->>>", request_payload)  
            sso_url = get_sso_url(request_payload)
            print("coverfox sso_url:----->>>", sso_url)  
            if not sso_url:
                return build_response(
                    False,
                    HTTP_ERROR_MESSAGES[404],
                    status_code=status.HTTP_404_NOT_FOUND)

            return build_response(
                True,
                "SSO URL generated successfully.",
                data={"sso_url": sso_url})
        except HTTPError as e:
            status_code = getattr(e.response, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
            return build_response(
                False,
                HTTP_ERROR_MESSAGES.get(status_code, "Request failed."),
                status_code=status_code)

        except Exception as exc:
            logger.exception("Unexpected error in CoverFoxView.post: %s", exc)
            return build_response(
                False,
                HTTP_ERROR_MESSAGES[500],
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


