from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from onboarding_v2.models import ApplicationV2
from utils.responseHandler import HttpResponse


class ApplicationTimelineView(APIView):
    permission_classes = []

    @extend_schema(
        tags=["Onboarding V2 History"],
        summary="Get Application Audit Timeline",
        description="Returns submission timestamp, full stage history, and status transition history for the specified application.",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request, application_id):
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.NotFound({"error": "Application not found"})

        status_history = application.status_history.select_related("changed_by").all()
        stage_snapshots = application.stage_snapshots.all().order_by("created_at")

        status_history_data = [
            {
                "id": str(h.id),
                "from_status": h.from_status,
                "to_status": h.to_status,
                "changed_by": (
                    h.changed_by.username or getattr(h.changed_by, "first_name", None)
                    if h.changed_by
                    else None
                ),
                "remarks": h.remarks,
                "timestamp": h.created_at.isoformat() if h.created_at else None,
            }
            for h in status_history
        ]

        stage_snapshots_data = [
            {
                "id": str(s.id),
                "stage": s.stage,
                "is_complete": s.is_complete,
                "payload": s.payload,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
                "modified_at": s.modified_at.isoformat() if s.modified_at else None,
            }
            for s in stage_snapshots
        ]

        submitted_at = application.submitted_at
        if not submitted_at:
            submitted_snap = stage_snapshots.filter(stage="SUBMITTED", is_complete=True).first()
            if submitted_snap and submitted_snap.completed_at:
                submitted_at = submitted_snap.completed_at

        data = {
            "application_id": application.application_id,
            "lead_code": application.lead.lead_code if application.lead else None,
            "customer_id": application.lead.customer_id if application.lead else None,
            "lending_partner": application.lending_partner,
            "current_stage": application.stage,
            "current_status": application.status,
            "created_at": application.created_at.isoformat() if application.created_at else None,
            "submitted_at": submitted_at.isoformat() if submitted_at else None,
            "modified_at": application.modified_at.isoformat() if application.modified_at else None,
            "status_history": status_history_data,
            "stage_snapshots": stage_snapshots_data,
        }

        return HttpResponse.Success(data)
