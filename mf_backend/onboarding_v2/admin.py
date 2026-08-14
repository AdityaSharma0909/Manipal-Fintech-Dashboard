from django import forms
from django.contrib import admin

from onboarding_v2.CreditScoreRange import CreditScoreRange
from onboarding_v2.constants import LeadType
from onboarding_v2.models import (
    AdditionalDetailsV2,
    AddressV2,
    ApplicationDocument,
    ApplicationStageSnapshot,
    ApplicationStatusHistory,
    ApplicationV2,
    Banner,
    BankLeadTrace,
    CorrectionOnboarding,
    BankBranch,
    BankDetailsV2,
    IdSequence,
    JewelleryItem,
    LeadAutoClosureSetting,
    LeadV2,
    LendingPartnerMaster,
    LoanPunchV2,
    Packet,
    PincodeMaster,
    SaasRequestLog,
    ThirdPartyLender,
    CustomerBankAccount,
    WebhookEvent,
    DailyGoldRate,
    RoiConfiguration,
    Customers,
    ProductV2,
    ProductV2AvailableFor,
)


class LendingPartnerMasterAdminForm(forms.ModelForm):
    available_for_lead_type = forms.MultipleChoiceField(
        label="Available for lead type",
        choices=(
            (LeadType.CO_LENDING, "Co-Lending"),
            (LeadType.FRESH, "Fresh"),
            (LeadType.BALANCE_TRANSFER, "BT"),
            (LeadType.SELF_LENDING, "Self Lending"),
        ),
        required=False,
        widget=forms.SelectMultiple(attrs={"size": 4}),
        help_text="Hold Control (Windows) or Command (Mac) to select multiple options.",
    )

    class Meta:
        model = LendingPartnerMaster
        fields = "__all__"


@admin.register(CreditScoreRange)
class CreditScoreRangeAdmin(admin.ModelAdmin):
    list_display = ("id", "min_score", "max_score", "score_band", "score_color")
    search_fields = ("score_band",)
    list_filter = ("score_band",)
    ordering = ("id",)


@admin.register(IdSequence)
class IdSequenceAdmin(admin.ModelAdmin):
    list_display = ("name", "last_value", "modified_at")
    search_fields = ("name",)


@admin.register(LeadV2)
class LeadV2Admin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "customer_id",
        "lead_code",
        "contact_number",
        "product_category",
        "product_subcategory",
        "lead_type",
        "lending_partner",
        "bank",
        "bank_branch",
        "status",
        "created_at",
    )
    search_fields = (
        "customer_name",
        "customer_id",
        "lead_code",
        "contact_number",
        "pan_number",
        "bank",
        "bank_branch",
    )
    list_filter = ("product_category", "product_subcategory", "lead_type", "status")
    ordering = ("-created_at",)


@admin.register(LeadAutoClosureSetting)
class LeadAutoClosureSettingAdmin(admin.ModelAdmin):
    list_display = (
        "lead_type",
        "product_subcategory",
        "auto_closure_days",
        "is_active",
        "modified_at",
        "created_at",
    )
    search_fields = ("lead_type", "product_subcategory")
    list_filter = ("lead_type", "product_subcategory", "is_active")
    ordering = ("lead_type", "product_subcategory")


class ApplicationStatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ("from_status", "to_status", "changed_by", "remarks", "created_at")
    can_delete = False


@admin.register(ApplicationV2)
class ApplicationV2Admin(admin.ModelAdmin):
    list_display = (
        "application_id",
        "lead",
        "status",
        "stage",
        "saas_status",
        "submitted_at",
        "created_at",
    )
    search_fields = ("application_id", "lead__customer_id", "lead__lead_code")
    list_filter = ("status", "stage", "saas_status")
    ordering = ("-created_at",)
    inlines = [ApplicationStatusHistoryInline]

    def save_model(self, request, obj, form, change):
        if getattr(request, "user", None) and request.user.is_authenticated:
            obj._status_changed_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("application", "from_status", "to_status", "changed_by", "created_at")
    list_filter = ("to_status", "from_status")
    search_fields = ("application__application_id", "remarks")
    ordering = ("-created_at",)


@admin.register(ApplicationStageSnapshot)
class ApplicationStageSnapshotAdmin(admin.ModelAdmin):
    list_display = ("application", "stage", "is_complete", "completed_at", "modified_at")
    list_filter = ("stage", "is_complete")
    search_fields = ("application__application_id",)




@admin.register(CorrectionOnboarding)
class CorrectionOnboardingAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "stage",
        "field_name",
        "image_id",
        "status",
        "created_at",
    )
    list_filter = ("stage", "status")
    search_fields = (
        "application__application_id",
        "field_name",
        "image_id",
    )
    ordering = ("-created_at",)


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ("application", "document_type", "subtype", "status", "created_at")
    list_filter = ("document_type", "status")
    search_fields = ("application__application_id", "document_type", "subtype")
    ordering = ("-created_at",)


@admin.register(AddressV2)
class AddressV2Admin(admin.ModelAdmin):
    list_display = ("application", "address_type", "pincode", "created_at")
    list_filter = ("address_type",)
    search_fields = ("application__application_id", "pincode")


@admin.register(BankDetailsV2)
class BankDetailsV2Admin(admin.ModelAdmin):
    list_display = ("application", "bank_name", "account_number", "ifsc_code", "created_at")
    search_fields = ("application__application_id", "bank_name", "account_number", "ifsc_code")


@admin.register(AdditionalDetailsV2)
class AdditionalDetailsV2Admin(admin.ModelAdmin):
    list_display = ("application", "is_employee", "nominee_full_name", "created_at")
    search_fields = ("application__application_id", "nominee_full_name")


@admin.register(Packet)
class PacketAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "packet_id", "barcode_id", "appraiser_id", "created_at")
    search_fields = ("application__application_id", "packet_id", "barcode_id", "appraiser_id")


@admin.register(JewelleryItem)
class JewelleryItemAdmin(admin.ModelAdmin):
    list_display = ("id", "packet", "type_of_jewellery", "number_of_articles", "created_at")
    search_fields = ("packet__application__application_id", "type_of_jewellery")


@admin.register(BankBranch)
class BankBranchAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "branch_name", "ifsc_code", "sol_id", "glo_id", "zone", "created_at")
    search_fields = ("bank_name", "branch_name", "ifsc_code", "sol_id", "glo_id", "pincode", "zone")
    list_filter = ("bank_name", "state", "district", "zone")


@admin.register(PincodeMaster)
class PincodeMasterAdmin(admin.ModelAdmin):
    list_display = ("pincode", "district", "statename", "created_at")
    search_fields = ("pincode", "district", "statename")


@admin.register(LendingPartnerMaster)
class LendingPartnerMasterAdmin(admin.ModelAdmin):
    form = LendingPartnerMasterAdminForm
    list_display = ("bank_name", "available_for", "available_for_lead_type", "bank_rate", "created_at")
    search_fields = ("bank_name", "available_for", "available_for_lead_type")
    list_filter = ("available_for",)


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("application_id", "status", "purpose", "retry_count", "created_at")
    list_filter = ("status", "purpose")
    search_fields = ("application_id", "request_id")
    ordering = ("-created_at",)


@admin.register(SaasRequestLog)
class SaasRequestLogAdmin(admin.ModelAdmin):
    list_display = ("application_identifier", "request_type", "attempts", "last_response_status", "last_attempt_at")
    list_filter = ("request_type",)
    search_fields = ("application_identifier",)
    ordering = ("-last_attempt_at",)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "is_active", "created_at", "modified_at")
    search_fields = ("title", "message", "file_url")
    list_filter = ("status", "is_active",)
    readonly_fields = ("id", "created_at", "modified_at")
    ordering = ("-created_at",)


@admin.register(ProductV2)
class ProductV2Admin(admin.ModelAdmin):
    class ProductV2AdminForm(forms.ModelForm):
        available_for = forms.MultipleChoiceField(
            choices=ProductV2AvailableFor.choices,
            widget=forms.SelectMultiple(attrs={"size": 2}),
            help_text="Select one or both onboarding journeys.",
        )

        class Meta:
            model = ProductV2
            fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if self.instance and self.instance.pk:
                self.initial["available_for"] = self.instance.available_for or []

        def clean_available_for(self):
            return list(self.cleaned_data["available_for"])

    form = ProductV2AdminForm
    list_display = (
        "product_code",
        "category",
        "repayment_frequency",
        "tenure_months",
        "ltv",
        "interest_rate",
        "is_active",
    )
    search_fields = ("product_code", "category")
    list_filter = ("category", "repayment_frequency", "tenure_months", "is_active")
    readonly_fields = ("id", "created_at", "modified_at")
    ordering = ("category", "repayment_frequency", "tenure_months", "product_code")


@admin.register(BankLeadTrace)
class BankLeadTraceAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "bank_name",
        "contact_number",
        "lead_type",
        "crm_type",
        "status",
        "response_status_code",
        "bank_lead_id",
        "lead",
    )
    list_filter = ("status", "bank_name", "lead_type", "crm_type", "response_status_code", "created_at")
    search_fields = (
        "contact_number",
        "bank_name",
        "bank_lead_id",
        "error_message",
        "lead__lead_code",
        "lead__customer_name",
        "lead__contact_number",
    )
    readonly_fields = (
        "id",
        "lead",
        "created_by",
        "bank_name",
        "contact_number",
        "lead_type",
        "crm_type",
        "bank_api_url",
        "request_headers",
        "request_payload",
        "response_payload",
        "response_status_code",
        "bank_lead_id",
        "status",
        "error_message",
        "metadata",
        "created_at",
        "modified_at",
    )
    fieldsets = (
        ("Summary", {
            "fields": (
                "id",
                "status",
                "bank_name",
                "contact_number",
                "lead_type",
                "crm_type",
                "bank_lead_id",
                "response_status_code",
                "lead",
                "created_by",
                "created_at",
                "modified_at",
            )
        }),
        ("Bank API Call", {
            "fields": (
                "bank_api_url",
                "request_headers",
                "request_payload",
                "response_payload",
                "error_message",
            )
        }),
        ("Onboarding Context", {
            "fields": ("metadata",),
        }),
    )
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False


@admin.register(LoanPunchV2)
class LoanPunchV2Admin(admin.ModelAdmin):
    list_display = (
        "application",
        "loan_account_number",
        "loan_account_document",
        "product_approval_screenshot",
        "bank_name",
        "approval_status",
        "is_bank_changed",
        "new_bank_name",
        "rejection_reason",
        "agent_id",
        "agent_name",
        "sanctioned_amount",
        "disbursed_amount",
        "created_at",
    )
    search_fields = ("application__application_id", "loan_account_number", "bank_name", "crm_id", "new_bank_name", "rejection_reason")
    list_filter = ("approval_status", "bank_name", "is_bank_changed", "is_agriculture")
    ordering = ("-created_at",)


@admin.register(ThirdPartyLender)
class ThirdPartyLenderAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "ifsc_code", "branch")
    search_fields = ("bank_name", "ifsc_code", "branch")
    list_filter = ("bank_name",)


@admin.register(CustomerBankAccount)
class CustomerBankAccountAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "ifsc_code", "branch")
    search_fields = ("bank_name", "ifsc_code", "branch")
    list_filter = ("bank_name",)


@admin.register(DailyGoldRate)
class DailyGoldRateAdmin(admin.ModelAdmin):
    list_display = ("product_type", "carat", "gold_rate", "bank", "created_at")
    search_fields = ("product_type", "carat", "bank")
    list_filter = ("product_type", "carat", "bank")
    ordering = ("product_type", "carat", "bank")


@admin.register(RoiConfiguration)
class RoiConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "lead_type",
        "bank",
        "product_type",
        "tenure",
        "repayment_schedule",
        "loan_range",
        "bank_roi",
        "manipal_roi",
        "blended_roi",
        "created_at",
    )
    search_fields = ("lead_type", "bank", "product_type", "tenure", "repayment_schedule", "loan_range")
    list_filter = ("lead_type", "bank", "product_type", "tenure", "repayment_schedule", "loan_range")
    ordering = ("lead_type", "bank", "product_type", "tenure", "repayment_schedule", "loan_range")


@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    list_display = ("customer_id", "fl_id", "name", "phone_number", "masked_pan_number", "is_defaulter", "created_at")
    search_fields = ("customer_id", "fl_id", "name", "phone_number", "pan_number")
    list_filter = ("is_defaulter",)
    ordering = ("-created_at",)

    @admin.display(description="PAN Number", ordering="pan_number")
    def masked_pan_number(self, obj):
        pan = (obj.pan_number or "").strip()
        if len(pan) <= 4:
            return "****" if pan else ""
        return f"{pan[:2]}{'*' * (len(pan) - 4)}{pan[-2:]}"
