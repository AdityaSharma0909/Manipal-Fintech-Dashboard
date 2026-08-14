# urls.py
from django.urls import path
from .views import (
    LeegalityTemplateSignRequestView,LeegalityTransactionStatusView,LeegalityUserEsignStatusView,
    LeegalityDeleteDocumentView,LeegalitySearchDocumentsView,
    LeegalityReactivateDocumentView,LeegalityResendNotificationView,
    LeegalityDeleteInvitationView,LeegalityMarkDocumentCompleteView,
    LeegalityDocumentDetailsView,LeegalityCompletedDocumentsView,
    LeegalityDocSignerSignView,LeegalityStampDetailsView,
    LeegalityStampGroupsView,LeegalityWebhookView
)
urlpatterns = [
    path('template-sign/', LeegalityTemplateSignRequestView.as_view(), name='leegality-template-sign'),
    path('transaction-status/', LeegalityTransactionStatusView.as_view(), name='leegality-transaction-status'),
    path('user-esign-status/', LeegalityUserEsignStatusView.as_view(), name='leegality-user-esign-status'),
    path("delete-document/", LeegalityDeleteDocumentView.as_view(), name="delete-document"),
    path('search/', LeegalitySearchDocumentsView.as_view(), name='leegality-search'),
    path('reactivate/', LeegalityReactivateDocumentView.as_view(), name='leegality-reactivate'),
    path('resend-notification/', LeegalityResendNotificationView.as_view(), name='leegality-resend-notification'),
    path('delete-invitation/', LeegalityDeleteInvitationView.as_view(), name='leegality-delete-invitation'),
    path('mark-complete/', LeegalityMarkDocumentCompleteView.as_view(), name='leegality-mark-complete'),
    path('document-details/', LeegalityDocumentDetailsView.as_view(), name='leegality-document-details'),
    path('completed-documents/', LeegalityCompletedDocumentsView.as_view(), name='leegality-completed-documents'),
    path('docsigner/sign/', LeegalityDocSignerSignView.as_view(), name='leegality-docsigner-sign'),
    path('stamp-details/', LeegalityStampDetailsView.as_view(), name='leegality-stamp-details'),
    path('stamp-groups/', LeegalityStampGroupsView.as_view(), name='leegality-stamp-groups'),
    path("webhook/",LeegalityWebhookView.as_view(),name="leegality_webhook"),



]
