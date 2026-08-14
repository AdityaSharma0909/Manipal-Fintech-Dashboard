from django.urls import path

from crif_bureau.views.crif_report_view import CrifReportView
from crif_bureau.views.views import (
    PhoneToPanView,
    CreateBureauConsentView,
    CrifBureauWebhookView,
)

urlpatterns = [
    path("bureau_report/", CrifReportView.as_view(), name="crif_phone_to_pan"),
    # path("phone-to-pan/", PhoneToPanView.as_view(), name="crif_phone_to_pan"),
    # path("create-bureau-consent/", CreateBureauConsentView.as_view(), name="crif_create_consent"),
    # path("webhook/<str:phone_number>/", CrifBureauWebhookView.as_view(), name="crif_bureau_webhook_with_phone"),
    # path("webhook/", CrifBureauWebhookView.as_view(), name="crif_bureau_webhook"),
]
