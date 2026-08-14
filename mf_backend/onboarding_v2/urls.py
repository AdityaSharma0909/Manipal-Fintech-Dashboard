from django.urls import path

from onboarding_v2.views.history import ApplicationTimelineView
from onboarding_v2.views import (
    OnboardingHealthView,
    LeadCreateView,
    LeadAutoClosureSettingView,
    ApplicationCreateView,
    StageUpdateView,
    BankBranchListCreateView,
    BankBranchDetailView,
    BankBranchFilterView,
    PincodeListView,
    PincodeDetailView,
    ApplicationStateView,
    FinalizeApplicationView,
    CorrectionRaiseView,
    RHActionView,
    AdminImportPincodesView,
    AdminImportBranchesView,
    PreScreenStatusWebhookView,
    SubmitApplicationView,
    PresignDocumentUploadView,
    LeadListView,
    ApplicationListView,
    PresignDocumentDownloadView,
    JewelleryPresignView,
    OnboardingDashboardView,
    ValidatePanView,
    AadhaarVerifyView,
    BankVerifyView,
    CustomerDefaulterCheckView,
    UniqueBankListView,
    DistrictListView,
    LendingPartnerListCreateView,
    AbleCreditSessionView,
    BTApplicationJourneyView,
    FundRefundStatementView,
    LendingPartnerDetailView,
    ThirdPartyLenderListCreateView,
    ThirdPartyLenderDetailView,
    CustomerBankAccountListView,
    DailyGoldRateAuditHistoryView,
    DailyGoldRateListCreateView,
    DailyGoldRateDetailView,
    RoiConfigurationListCreateView,
    RoiConfigurationDetailView,
    PincodeBranchLookupView,
    BannerUploadView,
    BannerListView,
    BannerDetailView,
    ProductV2ListView,
)
from onboarding_v2.views.loan_punch import LoanPunchView
from onboarding_v2.views.stages import EligibilityCheckView
from onboarding_v2.views.export import ExportApplicationV2View
from onboarding_v2.views.export_multi_table import ExportMultiTableView
from onboarding_v2.views.export_bt_transfer import ExportBTTransferReportView
from onboarding_v2.views.export_bt_disbursal import ExportBTDisbursalReportView
from onboarding_v2.views.export_new_gl_against_bt import ExportNewGLAgainstBTReportView
from onboarding_v2.views.export_tele_centre_report import ExportTeleCentreReportView

urlpatterns = [
    path("health/", OnboardingHealthView.as_view(), name="onboarding_v2_health"),
    path("dashboard/", OnboardingDashboardView.as_view(), name="onboarding_v2_dashboard"),
    path("leads/", LeadCreateView.as_view(), name="onboarding_v2_lead_create"),
    path("leads/settings/", LeadAutoClosureSettingView.as_view(), name="onboarding_v2_lead_auto_closure_settings"),
    
    path("leads/list/", LeadListView.as_view(), name="onboarding_v2_lead_list"),
    path("applications/", ApplicationCreateView.as_view(), name="onboarding_v2_application_create"),
    path("products/", ProductV2ListView.as_view(), name="onboarding_v2_product_list"),
    path("applications/list/", ApplicationListView.as_view(), name="onboarding_v2_application_list"),
    path("applications/export/", ExportApplicationV2View.as_view(), name="onboarding_v2_application_export"),
    path("applications/export/multi-table/", ExportMultiTableView.as_view(), name="onboarding_v2_multi_table_export"),
    path("applications/export/bt-transfer/", ExportBTTransferReportView.as_view(), name="onboarding_v2_bt_transfer_export"),
    path("applications/export/bt-disbursal/", ExportBTDisbursalReportView.as_view(), name="onboarding_v2_bt_disbursal_export"),
    path("applications/export/new-gl-against-bt/", ExportNewGLAgainstBTReportView.as_view(), name="onboarding_v2_new_gl_against_bt_export"),
    path("applications/export/tele-centre-report/", ExportTeleCentreReportView.as_view(), name="onboarding_v2_tele_centre_report_export"),
    path(
        "applications/<str:application_id>/stage/",
        StageUpdateView.as_view(),
        name="onboarding_v2_stage_update",
    ),
    path(
        "applications/<str:application_id>/eligibility-check/",
        EligibilityCheckView.as_view(),
        name="onboarding_v2_eligibility_check",
    ),
    path(
        "applications/<str:application_id>/fund-refund-statement/",
        FundRefundStatementView.as_view(),
        name="onboarding_v2_fund_refund_statement",
    ),
    path(
        "applications/<str:application_id>/submit/",
        SubmitApplicationView.as_view(),
        name="onboarding_v2_submit",
    ),
    path(
        "applications/<str:application_id>/correction/",
        CorrectionRaiseView.as_view(),
        name="onboarding_v2_correction_raise",
    ),
    path(
        "applications/<str:application_id>/rh-action/",
        RHActionView.as_view(),
        name="onboarding_v2_rh_action",
    ),
    path(
        "applications/<str:application_id>/aadhaar-verify/",
        AadhaarVerifyView.as_view(),
        name="onboarding_v2_aadhaar_verify",
    ),
    path(
        "applications/<str:application_id>/bank-verification-lite/",
        BankVerifyView.as_view(),
        name="onboarding_v2_bank_verify",
    ),
    path(
        "applications/loan-punch/",
        LoanPunchView.as_view(),
        name="onboarding_v2_loan_punch",
    ),
    path(
        "webhooks/saastech/pre-screen/",
        PreScreenStatusWebhookView.as_view(),
        name="onboarding_v2_prescreen_webhook",
    ),
    path(
        "bank-branches/",
        BankBranchListCreateView.as_view(),
        name="onboarding_v2_bank_branch_list",
    ),
    path(
        "bank-branches/filter/",
        BankBranchFilterView.as_view(),
        name="onboarding_v2_bank_branch_filter",
    ),
    path(
        "pincodes/",
        PincodeListView.as_view(),
        name="onboarding_v2_pincode_list",
    ),
    path(
        "bank-branches/<uuid:branch_id>/",
        BankBranchDetailView.as_view(),
        name="onboarding_v2_bank_branch_detail",
    ),
    path(
        "pincodes/<str:pincode>/",
        PincodeDetailView.as_view(),
        name="onboarding_v2_pincode_detail",
    ),

    path(
        "applications/<str:application_id>/state/",
        ApplicationStateView.as_view(),
        name="onboarding_v2_application_state",
    ),
    path(
        "applications/<str:application_id>/timeline/",
        ApplicationTimelineView.as_view(),
        name="onboarding_v2_application_timeline",
    ),
    path(
        "applications/<str:application_id>/finalize/",
        FinalizeApplicationView.as_view(),
        name="onboarding_v2_finalize",
    ),
    
    path(
        "applications/<str:application_id>/documents/presign/",
        PresignDocumentUploadView.as_view(),
        name="onboarding_v2_presign_document",
    ),
    path(
        "applications/<str:application_id>/documents/presign-get/",
        PresignDocumentDownloadView.as_view(),
        name="onboarding_v2_presign_document_get",
    ),
    path(
        "applications/<str:application_id>/jewellery/presign/",
        JewelleryPresignView.as_view(),
        name="onboarding_v2_jewellery_presign",
    ),
    path(
        "admin/pincodes/import/",
        AdminImportPincodesView.as_view(),
        name="onboarding_v2_import_pincodes",
    ),
    path(
        "admin/branches/import/",
        AdminImportBranchesView.as_view(),
        name="onboarding_v2_import_branches",
    ),
    path(
        "validate-pan/",
        ValidatePanView.as_view(),
        name="onboarding_v2_validate_pan",
    ),
    path(
        "customers/defaulter-check/",
        CustomerDefaulterCheckView.as_view(),
        name="onboarding_v2_customer_defaulter_check",
    ),
    path(
        "unique-banks/",
        UniqueBankListView.as_view(),
        name="onboarding_v2_unique_banks",
    ),
    path(
        "lending-partners/",
        LendingPartnerListCreateView.as_view(),
        name="onboarding_v2_lending_partners",
    ),
    path(
        "lending-partners/<uuid:partner_id>/",
        LendingPartnerDetailView.as_view(),
        name="onboarding_v2_lending_partner_detail",
    ),
    path(
        "third-party-lenders/",
        ThirdPartyLenderListCreateView.as_view(),
        name="onboarding_v2_third_party_lenders",
    ),
    path(
        "third-party-lenders/<int:lender_id>/",
        ThirdPartyLenderDetailView.as_view(),
        name="onboarding_v2_third_party_lender_detail",
    ),
    path(
        "customer-bank-accounts/",
        CustomerBankAccountListView.as_view(),
        name="onboarding_v2_customer_bank_accounts",
    ),
    path(
        "districts/",
        DistrictListView.as_view(),
        name="onboarding_v2_districts",
    ),
    path(
        "applications/<str:application_id>/able-credit/session/",
        AbleCreditSessionView.as_view(),
        name="onboarding_v2_able_credit_session",
    ),
    path(
        "applications/<str:application_id>/journey/",
        BTApplicationJourneyView.as_view(),
        name="onboarding_v2_bt_journey",
    ),
    path(
        "daily-gold-rates/",
        DailyGoldRateListCreateView.as_view(),
        name="onboarding_v2_daily_gold_rates",
    ),
    path(
        "daily-gold-rates/audit-history/",
        DailyGoldRateAuditHistoryView.as_view(),
        name="onboarding_v2_daily_gold_rate_audit_history",
    ),

    path(
        "daily-gold-rates/<uuid:rate_id>/",
        DailyGoldRateDetailView.as_view(),
        name="onboarding_v2_daily_gold_rate_detail",
    ),
    path(
        "roi-configurations/",
        RoiConfigurationListCreateView.as_view(),
        name="onboarding_v2_roi_configurations",
    ),
    path(
        "roi-configurations/<uuid:config_id>/",
        RoiConfigurationDetailView.as_view(),
        name="onboarding_v2_roi_configuration_detail",
    ),
    path(
        "pincode-branch-lookup/",
        PincodeBranchLookupView.as_view(),
        name="onboarding_v2_pincode_branch_lookup",
    ),
    # ── Banner endpoints ─────────────────────────────────────────────────
    path(
        "banners/upload/",
        BannerUploadView.as_view(),
        name="onboarding_v2_banner_upload",
    ),
    path(
        "banners/",
        BannerListView.as_view(),
        name="onboarding_v2_banner_list",
    ),
    path(
        "banners/<uuid:banner_id>/",
        BannerDetailView.as_view(),
        name="onboarding_v2_banner_detail",
    ),
]
