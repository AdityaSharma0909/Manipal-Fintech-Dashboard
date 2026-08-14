"""Module package for onboarding_v2 view implementations."""

from onboarding_v2.views.common import DefaultPagination, OnboardingHealthView
from onboarding_v2.views.leads import (
    ApplicationCreateView,
    ApplicationListView,
    LeadAutoClosureSettingView,
    LeadCreateView,
    LeadListView,
    OnboardingDashboardView,
    BTApplicationJourneyView,
)
from onboarding_v2.views.stages import (
    ApplicationStateView,
    CorrectionRaiseView,
    FinalizeApplicationView,
    StageUpdateView,
    SubmitApplicationView,
    ValidatePanView,
    AadhaarVerifyView,
    BankVerifyView,
    CustomerDefaulterCheckView,
    EligibilityCheckView,
    FundRefundStatementView,
    RHActionView
)
from onboarding_v2.views.presign import (
    JewelleryPresignView,
    PresignDocumentDownloadView,
    PresignDocumentUploadView,
)
from onboarding_v2.views.webhooks import PreScreenStatusWebhookView
from onboarding_v2.views.able_credit import AbleCreditSessionView
from onboarding_v2.views.export import ExportApplicationV2View
from onboarding_v2.views.export_multi_table import ExportMultiTableView
from onboarding_v2.views.export_bt_transfer import ExportBTTransferReportView
from onboarding_v2.views.export_bt_disbursal import ExportBTDisbursalReportView
from onboarding_v2.views.export_new_gl_against_bt import ExportNewGLAgainstBTReportView
from onboarding_v2.views.export_tele_centre_report import ExportTeleCentreReportView
from onboarding_v2.views.banner import (
    BannerUploadView,
    BannerListView,
    BannerDetailView,
)
from onboarding_v2.views.products import ProductV2ListView
from onboarding_v2.views.admin import (
    AdminImportBranchesView,
    AdminImportPincodesView,
    BankBranchDetailView,
    BankBranchFilterView,
    BankBranchListCreateView,
    DailyGoldRateAuditHistoryView,
    DailyGoldRateDetailView,
    DailyGoldRateListCreateView,
    RoiConfigurationListCreateView,
    RoiConfigurationDetailView,
    PincodeDetailView,
    PincodeListView,
    UniqueBankListView,
    DistrictListView,
    LendingPartnerListCreateView,
    LendingPartnerDetailView,
    ThirdPartyLenderListCreateView,
    ThirdPartyLenderDetailView,
    CustomerBankAccountListView,
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
    "OnboardingDashboardView",
    "StageUpdateView",
    "EligibilityCheckView",
    "SubmitApplicationView",
    "ApplicationStateView",
    "CorrectionRaiseView",
    "RHActionView",
    "FinalizeApplicationView",
    "ValidatePanView",
    "AadhaarVerifyView",
    "BankVerifyView",
    "CustomerDefaulterCheckView",
    "PresignDocumentUploadView",
    "PresignDocumentDownloadView",
    "JewelleryPresignView",
    "PreScreenStatusWebhookView",
    "BankBranchListCreateView",
    "BankBranchDetailView",
    "BankBranchFilterView",
    "PincodeListView",
    "PincodeDetailView",
    "AdminImportPincodesView",
    "AdminImportBranchesView",
    "UniqueBankListView",
    "DistrictListView",
    "LendingPartnerListCreateView",
    "LendingPartnerDetailView",
    "ThirdPartyLenderListCreateView",
    "ThirdPartyLenderDetailView",
    "CustomerBankAccountListView",
    "DailyGoldRateListCreateView",
    "DailyGoldRateAuditHistoryView",
    "DailyGoldRateDetailView",
    "RoiConfigurationListCreateView",
    "RoiConfigurationDetailView",
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
    "LeadAutoClosureSettingView",
    "AbleCreditSessionView",
    "BTApplicationJourneyView",
    "ExportApplicationV2View",
    "ExportMultiTableView",
    "ExportBTTransferReportView",
    "ExportBTDisbursalReportView",
    "ExportNewGLAgainstBTReportView",
    "ExportTeleCentreReportView",
    "BannerUploadView",
    "BannerListView",
    "BannerDetailView",
    "ProductV2ListView",
]

_LAZY_EXPORTS = {
    "enqueue_pre_screen": ("onboarding_v2.helpers.saas_helpers", "enqueue_pre_screen"),
    "enqueue_create_loan": ("onboarding_v2.helpers.saas_helpers", "enqueue_create_loan"),
    "build_document_presign": ("onboarding_v2.helpers.presign_helpers", "build_document_presign"),
    "build_document_download_presign": (
        "onboarding_v2.helpers.presign_helpers",
        "build_document_download_presign",
    ),
    "notify_app_step_error": ("onboarding_v2.notifications", "notify_app_step_error"),
    "notify_saas_alert": ("onboarding_v2.notifications", "notify_saas_alert"),
    "verify_pan_number": ("onboarding_v2.services", "verify_pan_number"),
    "run_bureau_check_task": ("onboarding_v2.tasks", "run_bureau_check_task"),
    "create_application": ("onboarding_v2.helpers.lead_application_helpers", "create_application"),
    "ApplicationStageSnapshot": ("onboarding_v2.models", "ApplicationStageSnapshot"),
}


def __getattr__(name):
    target = _LAZY_EXPORTS.get(name)
    if not target:
        raise AttributeError(f"module 'onboarding_v2.views' has no attribute {name!r}")
    module_path, attr = target
    module = __import__(module_path, fromlist=[attr])
    value = getattr(module, attr)
    globals()[name] = value
    return value
