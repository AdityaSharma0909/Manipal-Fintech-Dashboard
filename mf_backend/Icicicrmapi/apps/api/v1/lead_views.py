"""
apps/api/v1/lead_views.py
==========================
API View for pushing a customer lead to the ICICI CRM system.

Authentication: TEMPORARILY DISABLED (AllowAny + no auth classes)
for public testing. Re-enable by inheriting from ``BaseAPIView``
and removing the class-level overrides.
"""

import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

from apps.api.v1.views import BaseAPIView
from apps.api.v1.lead_serializers import (
    LeadPushRequestSerializer,
    LeadPushSuccessResponseSerializer,
)
from apps.business.services.lead_service import LeadService
from apps.data.repositories.lead_repository import LeadRepository
from apps.data.repositories.log_repository import (
    RequestLogRepository,
    ResponseLogRepository,
)
from apps.data.repositories.app_settings_repository import AppSettingsRepository
from apps.validators.lead_validator import LeadValidator
from apps.integrations.icici.lead_client import ICICILeadClient

logger = logging.getLogger(__name__)


class IciciCrmLeadView(BaseAPIView):
    """
    POST /api/v1/icici-crm/push-lead/

    Accepts a ``CustomerCrmDetails`` JSON payload, validates it, persists the
    lead locally, and forwards it to the ICICI CRM integration API.

    .. note::
        Authentication is **temporarily removed** for integration testing.
        Re-enable by removing ``authentication_classes`` and
        ``permission_classes`` overrides below.
    """

    # -------------------------------------------------------------------------
    # TEMPORARY: Remove auth for public testing
    # -------------------------------------------------------------------------
    authentication_classes = []          # No JWT / session auth required
    permission_classes = [AllowAny]      # Open to all callers

    # -------------------------------------------------------------------------
    # Dependency injection (manual wiring — replace with DI container later)
    # -------------------------------------------------------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service = LeadService(
            lead_repo=LeadRepository(),
            request_log_repo=RequestLogRepository(),
            response_log_repo=ResponseLogRepository(),
            settings_repo=AppSettingsRepository(),
            validator=LeadValidator(),
            icici_client=ICICILeadClient(),
        )

    # -------------------------------------------------------------------------
    # Swagger / OpenAPI schema
    # -------------------------------------------------------------------------
    @extend_schema(
        summary="Push Lead to ICICI CRM [Public]",
        description=(
            "Accepts customer details, validates them, persists the lead, and "
            "forwards it to the ICICI CRM integration API.\n\n"
            "**Authentication:** Temporarily disabled for testing — no JWT required."
        ),
        request=LeadPushRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=LeadPushSuccessResponseSerializer,
                description="Lead accepted and forwarded to ICICI CRM successfully.",
                examples=[
                    OpenApiExample(
                        name="Success",
                        value={"success": True, "message": "Lead pushed successfully."},
                        response_only=True,
                        status_codes=["200"],
                    )
                ],
            ),
            400: OpenApiResponse(
                description="ICICI CRM downstream rejection or business-rule failure.",
                examples=[
                    OpenApiExample(
                        name="Downstream Failure",
                        value={
                            "success": False,
                            "message": "Failed to push lead to ICICI CRM.",
                        },
                        response_only=True,
                        status_codes=["400"],
                    )
                ],
            ),
            422: OpenApiResponse(
                description="Validation error — one or more fields are invalid.",
                examples=[
                    OpenApiExample(
                        name="Validation Errors",
                        value={
                            "firstName": ["First name must not contain numbers."],
                            "mobileNumber": [
                                "Invalid mobile number. Must be exactly 10 digits "
                                "and start with 6, 7, 8, or 9."
                            ],
                            "bankId": [
                                "Ensure this value is greater than or equal to 1."
                            ],
                        },
                        response_only=True,
                        status_codes=["422"],
                    )
                ],
            ),
        },
        examples=[
            OpenApiExample(
                name="Valid Lead Payload",
                summary="Minimal valid request body",
                value={
                    "userId": "USR001",
                    "bankId": 1,
                    "firstName": "Sourav",
                    "lastName": "Gupta",
                    "mobileNumber": "9876543210",
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Without userId (userId is optional)",
                value={
                    "bankId": 1,
                    "firstName": "Priya",
                    "lastName": "Sharma",
                    "mobileNumber": "8765432109",
                },
                request_only=True,
            ),
        ],
        tags=["ICICI CRM"],
    )
    def post(self, request):
        """
        Push customer CRM details to ICICI.

        Steps:
          1. Deserialize + validate request body via ``LeadPushRequestSerializer``.
          2. Delegate to ``LeadService.push_lead_to_crm`` for business logic.
          3. Return a structured success or failure response.
        """
        # 1. Deserialize / validate
        serializer = LeadPushRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Business layer
        correlation_id = self.get_correlation_id(request)

        logger.info(
            "[%s] Received push-lead request for mobile: %s",
            correlation_id,
            serializer.validated_data.get("mobile_number", "N/A"),
        )

        result = self._service.push_lead_to_crm(
            serializer.validated_data,
            correlation_id,
        )

        # 3. Build response
        if result.get("success", False):
            return Response(
                {"success": True, "message": "Lead pushed successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": result.get(
                    "message", "Failed to push lead to ICICI CRM."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
