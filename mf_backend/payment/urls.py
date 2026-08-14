from django.urls import path

# from payment.views.test_view import TestView
from payment.views.cipherpay_view import CipherpayGenerateQR, CipherpayInitiateCollect, CipherpayGenerateIntentURL, CipherpayStatusView
from payment.views.callback import CipherpayUPICallback
from payment.views.cipherpay_status import cipherpayStatus
from payment.views.paymentView import PaymentView
from payment.views.sales_officer_payout import SalesOfficerPayoutUploadView, SalesOfficerCommissionListView, SalesOfficerIncentiveListView, AgentDashboardView

from payment.views.imoneypay_view import IMoneyPayGenerateQR, IMoneyPayStatusView
from payment.views.callback import IMoneyPayCallback

urlpatterns = [
    path("upi/callback/", CipherpayUPICallback.as_view()),
    path("cipherpay/generate-qr", CipherpayGenerateQR.as_view()),
    path("cipherpay/generate-intent-url", CipherpayGenerateIntentURL.as_view()),
    path("cipherpay/initiate-collect", CipherpayInitiateCollect.as_view()),
    path("cipherpay/status", CipherpayStatusView.as_view()),
    path("status/", cipherpayStatus.as_view()),
    path("", PaymentView.as_view()),

    path("imoneypay/generate-qr/", IMoneyPayGenerateQR.as_view()),
    path("imoneypay/callback/", IMoneyPayCallback.as_view()),
    path("imoneypay/status/", IMoneyPayStatusView.as_view()),
    path("sales-officer/upload/<str:upload_type>/", SalesOfficerPayoutUploadView.as_view()),
    path("agent/commission/", SalesOfficerCommissionListView.as_view()),
    path("sales-officer/incentive/", SalesOfficerIncentiveListView.as_view()),
    path("agent/dashboard/", AgentDashboardView.as_view()),
]
