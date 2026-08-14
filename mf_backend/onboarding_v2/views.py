"""View aggregator.

This module re-exports view classes so existing imports remain stable while
implementation lives in smaller modules.
"""

from onboarding_v2.views.common import DefaultPagination, OnboardingHealthView
from onboarding_v2.views.leads import (
    ApplicationCreateView,
    ApplicationListView,
    LeadCreateView,
    LeadListView,
)
from onboarding_v2.views.stages import (
    ApplicationStateView,
    FinalizeApplicationView,
    StageUpdateView,
    SubmitApplicationView, EligibilityCheckView,FundRefundStatementView
)
from onboarding_v2.views.presign import (
    JewelleryPresignView,
    PresignDocumentDownloadView,
    PresignDocumentUploadView,
)
from onboarding_v2.views.webhooks import PreScreenStatusWebhookView
from onboarding_v2.views.admin import (
    AdminImportBranchesView,
    AdminImportPincodesView,
    BankBranchDetailView,
    BankBranchListCreateView,
    PincodeDetailView,
    PincodeListView,
    UniqueBankNamesView,
    BankBranchFilterView,
    PincodeBranchLookupView,
)
from onboarding_v2.helpers.saas_helpers import enqueue_create_loan, enqueue_pre_screen
from onboarding_v2.helpers.presign_helpers import (
    build_document_download_presign,
    build_document_presign,
)
from onboarding_v2.notifications import notify_app_step_error, notify_saas_alert
from onboarding_v2.services import verify_pan_number
from onboarding_v2.tasks import run_bureau_check_task
from onboarding_v2.helpers.lead_application_helpers import create_application
from onboarding_v2.models import ApplicationStageSnapshot

__all__ = [
    "DefaultPagination",
    "OnboardingHealthView",
    "LeadCreateView",
    "LeadListView",
    "ApplicationCreateView",
    "ApplicationListView",
    "StageUpdateView",
    "EligibilityCheckView",
    "FundRefundStatementView",
    "SubmitApplicationView",
    "ApplicationStateView",
    "FinalizeApplicationView",
    "PresignDocumentUploadView",
    "PresignDocumentDownloadView",
    "JewelleryPresignView",
    "PreScreenStatusWebhookView",
    "BankBranchListCreateView",
    "BankBranchDetailView",
    "UniqueBankNamesView",
    "PincodeListView",
    "PincodeDetailView",
    "AdminImportPincodesView",
    "AdminImportBranchesView",
    "BankBranchFilterView",
    "PincodeBranchLookupView",
    "enqueue_pre_screen",
    "enqueue_create_loan",
    "build_document_presign",
    "build_document_download_presign",
    "notify_app_step_error",
    "notify_saas_alert",
    "verify_pan_number",
    "run_bureau_check_task",
    "create_application",
    "ApplicationStageSnapshot",

]
