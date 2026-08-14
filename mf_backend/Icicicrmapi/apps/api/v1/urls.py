from django.urls import path

from apps.api.v1.views import HealthCheckView
from apps.api.v1.lead_views import IciciCrmLeadView

app_name = "v1"

urlpatterns = [
    # -------------------------------------------------------------------------
    # Health / Liveness
    # -------------------------------------------------------------------------
    path("health/", HealthCheckView.as_view(), name="health"),

    # -------------------------------------------------------------------------
    # ICICI CRM Integration
    # -------------------------------------------------------------------------
    path(
        "icici-crm/push-lead/", 
        IciciCrmLeadView.as_view(), 
        name="icici-crm-push-lead"
    ),
]
