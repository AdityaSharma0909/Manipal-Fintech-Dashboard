"""AbleCredit views — session token generation."""
from __future__ import annotations

import logging

from rest_framework.views import APIView

from utils.responseHandler import HttpResponse
from onboarding_v2.constants import LeadType
from onboarding_v2.models import ApplicationV2
from onboarding_v2.able_credit import AbleCreditError, create_session, requires_video_pd

logger = logging.getLogger(__name__)


class AbleCreditSessionView(APIView):
    """
    POST /applications/<application_id>/able-credit/session/

    Returns an AbleCredit session token so the mobile app can initialise the
    video-PD SDK.  Only applicable to Balance Transfer applications where the
    requested loan amount is >= 10 Lac.
    """

    def post(self, request, application_id):
        try:
            application = ApplicationV2.objects.select_related("lead").get(
                application_id=application_id
            )
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        lead = application.lead
        if not lead or lead.lead_type != LeadType.BALANCE_TRANSFER:
            return HttpResponse.BadRequest(
                "AbleCredit session is only available for Balance Transfer applications"
            )

        if not requires_video_pd(application):
            return HttpResponse.BadRequest(
                "AbleCredit video PD is not required for loan amounts below 10 Lac"
            )

        try:
            result = create_session(application)
        except AbleCreditError as exc:
            logger.error(
                "AbleCredit session creation failed | app=%s | error=%s",
                application_id,
                exc,
            )
            return HttpResponse.InternalServerError(str(exc))

        return HttpResponse.Success(
            {
                "session_token": result["session_token"],
                "sdk_key": result["sdk_key"],
                "tenant_id": result["tenant_id"],
            }
        )
