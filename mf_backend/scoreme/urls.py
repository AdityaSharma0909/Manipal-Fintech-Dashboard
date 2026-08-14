from django.urls import path

from scoreme.views.bsa_analysis_views import UploadBankStatements
from scoreme.views.bsa_webhook import BsaWebhookView

urlpatterns =[
    path("bsa/",UploadBankStatements.as_view()),
    path("webhook",BsaWebhookView.as_view()),
]