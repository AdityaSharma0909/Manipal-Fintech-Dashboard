import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from crm_integration.serializers import (
    BranchByPincodeRequestSerializer,
    BranchByPincodeResponseSerializer,
    CreateBajajFinServoLeadInitialRequestSerializer,
    CreateLeadResultSerializer,
    CommonResponseSerializer
)
from crm_integration.services import CreateBajajFinServoLeadUseCase, MasterUseCase, TokenService

logger = logging.getLogger(__name__)


# GoldLoanTokenAuthentication intentionally excluded from migration scope.
# GoldLoanAuthorizationFilter intentionally excluded from migration scope.


class BajajFinServoLeadCreateView(APIView):
    """Validates lead request payload, executes integration, and maps the response back."""
    
    # GoldLoanTokenAuthentication excluded — open for local development.
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=CreateBajajFinServoLeadInitialRequestSerializer,
        responses={201: CommonResponseSerializer, 200: CommonResponseSerializer, 400: CommonResponseSerializer},
        summary="Create a new Bajaj FinServ Lead"
    )
    def post(self, request):
        logger.info("Lead creation view initiated")
        
        serializer = CreateBajajFinServoLeadInitialRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            # Match HandleValidationError in C# BaseApiController.cs
            first_error = ""
            for field, errors in serializer.errors.items():
                first_error = errors[0]
                break
            
            logger.warning(f"Validation failed: {serializer.errors}")
            return Response({
                "StatusCode": status.HTTP_400_BAD_REQUEST,
                "StatusMessage": first_error,
                "Data": "Validation failed."
            }, status=status.HTTP_400_BAD_REQUEST)
            
        validated_data = serializer.validated_data
        
        from asgiref.sync import async_to_sync
        
        usecase = CreateBajajFinServoLeadUseCase()
        result = async_to_sync(usecase.execute)(validated_data)
        
        logger.info(f"UseCase execute complete: status={result.get('Status')}")
        
        lead_status = (result.get('Status') or '').strip().lower()
        
        if lead_status == 'success':
            return Response({
                "StatusCode": status.HTTP_201_CREATED,
                "StatusMessage": "Successfully created a BajajFinServo Lead",
                "Data": result
            }, status=status.HTTP_201_CREATED)
            
        elif lead_status == 'duplicate':
            return Response({
                "StatusCode": status.HTTP_200_OK,
                "StatusMessage": "A lead for this mobile number already exists",
                "Data": result
            }, status=status.HTTP_200_OK)
            
        else:
            # Propagate the actual error status from the UseCase/API client.
            # BajajFinServoApiException carries its own status code (e.g. 500).
            # Map to the most appropriate HTTP error code rather than always 400.
            error_status = result.get('StatusCode', 400)
            if not isinstance(error_status, int) or error_status < 400 or error_status > 599:
                error_status = 400
            return Response({
                "StatusCode": error_status,
                "StatusMessage": result.get('Message') or "Failed to create a BajajFinServo Lead.",
                "Data": result
            }, status=error_status)


class MasterBranchView(APIView):
    """

    Fetches branches based on district query parameter.
    """
    
    # GoldLoanTokenAuthentication excluded — open for local development.
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: CommonResponseSerializer, 400: CommonResponseSerializer, 404: CommonResponseSerializer},
        summary="Fetch branch details by district ID"
    )
    def get(self, request):
        logger.info("GetBranch view initiated")
        
        district_id_str = request.query_params.get('districtId')
        if not district_id_str:
            return Response({
                "StatusCode": status.HTTP_400_BAD_REQUEST,
                "StatusMessage": "districtId is required.",
                "Data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            district_id = int(district_id_str)
        except ValueError:
            return Response({
                "StatusCode": status.HTTP_400_BAD_REQUEST,
                "StatusMessage": "districtId must be an integer.",
                "Data": None
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Execute repository query
        from asgiref.sync import async_to_sync
        usecase = MasterUseCase()
        result = async_to_sync(usecase.get_branches)(district_id)
        
        status_code = result.get('StatusCode', 500)
        
        if status_code != 200:
            # Mirror .NET MasterController: return 404 when no data found, otherwise use returned code.
            message = result.get('Message', 'Error fetching branch list')
            if message in ('No Data Found', 'No data found') or not result.get('Data'):
                http_code = 404
            elif status_code in [400, 404, 500]:
                http_code = status_code
            else:
                http_code = status.HTTP_400_BAD_REQUEST
            return Response({
                "StatusCode": http_code,
                "StatusMessage": message,
                "Data": result.get('Data')
            }, status=http_code)
            
        return Response({
            "StatusCode": status.HTTP_200_OK,
            "StatusMessage": result.get('Message', 'Success'),
            "Data": result.get('Data')
        }, status=status.HTTP_200_OK)


class BranchByPincodeView(APIView):
    """Fetch the available branches mapped to a supplied pincode."""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=BranchByPincodeRequestSerializer,
        responses={
            200: BranchByPincodeResponseSerializer,
            400: BranchByPincodeResponseSerializer,
            404: BranchByPincodeResponseSerializer
        },
        summary="Fetch available branches by pincode"
    )
    def post(self, request):
        logger.info("BranchByPincode view initiated")

        serializer = BranchByPincodeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Invalid pincode payload: %s", serializer.errors)
            return Response({
                "success": False,
                "message": "Invalid pincode",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        pincode = serializer.validated_data["pincode"]
        usecase = MasterUseCase()
        result = usecase.get_branches_by_pincode(pincode)

        if result.get("StatusCode") == status.HTTP_200_OK:
            return Response({
                "success": True,
                "message": result.get("Message", "Branches fetched successfully"),
                "data": result.get("Data", [])
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": result.get("Message", "No branches found for the given pincode"),
            "data": []
        }, status=status.HTTP_404_NOT_FOUND)


class TokenTestView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: CommonResponseSerializer},
        summary="Test token generation and print detailed debug info"
    )
    def get(self, request):
        import asyncio
        from asgiref.sync import async_to_sync

        provider_info = {}

        async def fetch_token():
            token_service = TokenService()
            provider = token_service.token_provider
            provider_info['type'] = type(provider).__name__
            token = await token_service.get_access_token()
            return token

        try:
            token = async_to_sync(fetch_token)()
            return Response({
                "StatusCode": 200,
                "StatusMessage": "Token generated successfully",
                "Data": {
                    "provider": provider_info.get('type'),
                    "token_preview": token[:80] + '...' if len(token) > 80 else token
                }
            }, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({
                "StatusCode": 500,
                "StatusMessage": f"Token generation failed: {str(ex)}",
                "Data": None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
