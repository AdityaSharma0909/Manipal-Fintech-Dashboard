import uuid

from django.conf import settings
from utils.envSetup import environment
from django.db import models
from django.core.validators import RegexValidator
from simple_history.models import HistoricalRecords

from onboarding_v2.constants import (
    AddressType,
    ApplicationStage,
    ApplicationStatus,
    BureauDecision,
    DocumentStatus,
    DocumentType,
    Gender,
    LendingPartner,
    LeadStatus,
    ProductSubCategory,
    ProductCategory,
    LeadSource,
    LeadType,
    ProofOfAddress,
    Relation,
    PrimaryBorrowerType,
    NriStatus,
)


def default_json():
    return {}

class IdSequence(models.Model):
    """
    Generic sequence holder for generating customer/lead/application IDs.
    """
    name = models.CharField(max_length=64, unique=True)
    last_value = models.PositiveIntegerField(default=0)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}:{self.last_value}"


class LeadV2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    lead_code = models.CharField(max_length=64, unique=True, blank=True, null=True)
    contact_number = models.CharField(max_length=20, db_index=True)
    email_address = models.CharField(max_length=255, blank=True, null=True)
    customer_name = models.CharField(max_length=255)
    product_category = models.CharField(
        max_length=32, choices=ProductCategory.choices, default=ProductCategory.LOAN
    )
    product_subcategory = models.CharField(
        max_length=64, choices=ProductSubCategory.choices, blank=True, null=True
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    source = models.CharField(
        max_length=32, choices=LeadSource.choices, default=LeadSource.SELF
    )
    lead_type = models.CharField(
        max_length=32, choices=LeadType.choices, blank=True, null=True
    )
    crm_type = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    lending_partner = models.CharField(max_length=255, blank=True, null=True)
    bank = models.CharField(max_length=255, blank=True, null=True)
    bank_branch = models.CharField(max_length=255, blank=True, null=True)
    BankLeadID = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(
        max_length=16, choices=Gender.choices, blank=True, null=True
    )
    dob = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    is_pan_verified = models.BooleanField(default=False)
    status = models.CharField(
        max_length=64,
        choices=LeadStatus.choices,
        default=LeadStatus.ACTIVE,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="onboarding_v2_leads",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="onboarding_v2_leads_created",
        null=True,
        blank=True,
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="onboarding_v2_leads_modified",
        null=True,
        blank=True,
    )
    parent_lead_code = models.CharField(max_length=64, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_name} ({self.customer_id})"


class ApplicationV2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_id = models.CharField(max_length=64, unique=True)
    lead = models.ForeignKey(
        LeadV2, on_delete=models.CASCADE, related_name="applications"
    )
    lending_partner = models.CharField(
        max_length=64,
        choices=LendingPartner.choices,
        default=LendingPartner.AXIS_BANK,
        null=True,
        blank=True,
    )
    loan_type = models.CharField(
        max_length=32, choices=LeadType.choices, blank=True, null=True
    )
    status = models.CharField(
        max_length=64,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
    )
    stage = models.CharField(
        max_length=64, choices=ApplicationStage.choices, default=ApplicationStage.PAN
    )
    partner_branch_code = models.CharField(max_length=64, blank=True, null=True)
    partner_branch_name = models.CharField(max_length=255, blank=True, null=True)
    client_loan_id = models.CharField(max_length=128, blank=True, null=True)
    partner_product_code = models.CharField(max_length=128, blank=True, null=True)
    agreement_id = models.CharField(max_length=128, blank=True, null=True)
    spread_id = models.CharField(max_length=128, blank=True, null=True)
    ltr = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    interest_start_date = models.DateField(blank=True, null=True)
    loan_maturity_date = models.DateField(blank=True, null=True)
    first_repayment_date = models.DateField(blank=True, null=True)
    primary_borrower_type = models.CharField(
        max_length=32, choices=PrimaryBorrowerType.choices, blank=True, null=True
    )
    nationality = models.CharField(max_length=64, blank=True, null=True)
    nri_status = models.CharField(
        max_length=1, choices=NriStatus.choices, blank=True, null=True
    )
    caste = models.CharField(max_length=64, blank=True, null=True)
    occupation = models.CharField(max_length=128, blank=True, null=True)
    applicant_profession = models.CharField(max_length=128, blank=True, null=True)
    income_source = models.CharField(max_length=128, blank=True, null=True)
    processing_fee = models.DecimalField(
        max_digits=14, decimal_places=2, blank=True, null=True
    )
    stamp_duty = models.DecimalField(
        max_digits=14, decimal_places=2, blank=True, null=True
    )
    insurance_charges = models.DecimalField(
        max_digits=14, decimal_places=2, blank=True, null=True
    )
    documentation_charges = models.DecimalField(
        max_digits=14, decimal_places=2, blank=True, null=True
    )
    other_charges = models.DecimalField(
        max_digits=14, decimal_places=2, blank=True, null=True
    )
    total_charges = models.DecimalField(
        max_digits=14, decimal_places=2, blank=True, null=True
    )
    number_of_animal_cattle = models.IntegerField(blank=True, null=True)
    consent_timestamp = models.DateTimeField(blank=True, null=True)
    consent_ip = models.GenericIPAddressField(blank=True, null=True)
    bureau_name = models.CharField(max_length=64, blank=True, null=True)
    bureau_report_link = models.CharField(max_length=512, blank=True, null=True)
    bureau_pull_date = models.DateField(blank=True, null=True)
    bureau_reference_number = models.CharField(max_length=128, blank=True, null=True)
    reference_number = models.CharField(max_length=128, blank=True, null=True)
    compliance = models.CharField(max_length=128, blank=True, null=True)
    source_id = models.CharField(max_length=64, blank=True, null=True)
    multi_appraisal = models.BooleanField(default=False)
    # Separate progress bars for pre-screen and post-screen
    pre_screen_completion = models.PositiveSmallIntegerField(default=0)
    post_screen_completion = models.PositiveSmallIntegerField(default=0)
    stage_payload = models.JSONField(default=default_json, blank=True)
    saas_request_id = models.CharField(max_length=128, blank=True, null=True)
    saas_status = models.CharField(max_length=64, blank=True, null=True)
    saas_prescreen_raw = models.JSONField(default=default_json, blank=True)
    saas_create_loan_status = models.CharField(max_length=64, blank=True, null=True)
    saas_create_loan_raw = models.JSONField(default=default_json, blank=True)
    saas_prescreen_remarks = models.TextField(blank=True, null=True)
    saas_loan_remarks = models.TextField(blank=True, null=True)
    saas_last_attempt_at = models.DateTimeField(blank=True, null=True)
    saas_attempts = models.PositiveIntegerField(default=0)
    saas_lead_id = models.CharField(max_length=128, blank=True, null=True)
    van_number = models.CharField(max_length=128, blank=True, null=True)
    bureau_score = models.IntegerField(blank=True, null=True)
    score_color = models.CharField(max_length=20, blank=True, null=True)
    bureau_decision = models.CharField(
        max_length=32,
        choices=BureauDecision.choices,
        default=BureauDecision.PENDING,
    )
    bureau_raw = models.JSONField(default=default_json, blank=True)
    rh_remarks = models.TextField(blank=True, null=True)
    rh_rejection_reason = models.CharField(max_length=255, blank=True, null=True)
    punched_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="applications_punched",
        null=True,
        blank=True,
    )
    assigned_rh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="applications_assigned_rh",
        null=True,
        blank=True,
    )
    parent_application_id = models.CharField(max_length=64, blank=True, null=True)
    submitted_at = models.DateTimeField(blank=True, null=True, help_text="Timestamp when application was submitted")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application_id}"


class CorrectionOnboarding(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RESOLVED = "RESOLVED", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        ApplicationV2, on_delete=models.CASCADE, related_name="corrections"
    )
    stage = models.CharField(max_length=64, choices=ApplicationStage.choices)
    field_name = models.CharField(max_length=255)
    image_id = models.CharField(max_length=128, blank=True, null=True)
    payload = models.JSONField(default=default_json, blank=True)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Correction for {self.application.application_id} - {self.stage}.{self.field_name}"


class ApplicationStageSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        ApplicationV2, on_delete=models.CASCADE, related_name="stage_snapshots"
    )
    stage = models.CharField(max_length=64, choices=ApplicationStage.choices)
    payload = models.JSONField(default=default_json, blank=True)
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("application", "stage")


class ApplicationStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        ApplicationV2, on_delete=models.CASCADE, related_name="status_history"
    )
    from_status = models.CharField(max_length=64, blank=True, null=True)
    to_status = models.CharField(max_length=64, choices=ApplicationStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="application_status_changes",
        null=True,
        blank=True,
    )
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Application status histories"

    def __str__(self):
        return f"{self.application.application_id}: {self.from_status} -> {self.to_status} at {self.created_at}"




class ApplicationDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        ApplicationV2, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(
        max_length=64, choices=DocumentType.choices, default=DocumentType.OTHER
    )
    subtype = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(
        max_length=32, choices=DocumentStatus.choices, default=DocumentStatus.UPLOADED
    )
    file = models.FileField(
        max_length=255, upload_to=settings.APPLICATION_DOCUMENT, blank=True, null=True
    )
    file_url = models.CharField(max_length=500, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="onboarding_v2_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document_type} for {self.application.application_id}"


class AddressV2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        ApplicationV2, on_delete=models.CASCADE, related_name="addresses"
    )
    address_type = models.CharField(
        max_length=32, choices=AddressType.choices, default=AddressType.PERMANENT
    )
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    address_line3 = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("application", "address_type")


class Packet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        ApplicationV2, on_delete=models.CASCADE, related_name="packets"
    )
    packet_id = models.CharField(max_length=128)
    barcode_id = models.CharField(max_length=128, blank=True, null=True)
    gross_weight = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    gross_value = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    net_adjusted_weight = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    net_adjusted_value = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    appraiser_id = models.CharField(max_length=128, blank=True, null=True)
    appraiser_name = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Packet {self.packet_id}"


def jewellery_upload_path(instance, filename):
    """
    Keep jewellery images under the same application folder in object storage.
    """
    app_id = None
    try:
        app_id = instance.packet.application.application_id
    except Exception:
        app_id = None
    env_prefix = environment.APP_ENV.lower() if getattr(environment, "APP_ENV", None) else "env"
    safe_app = app_id or "unknown_app"
    return f"{env_prefix}/manipal/{safe_app}/jewellery/{filename}"


class JewelleryItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    packet = models.ForeignKey(
        Packet, on_delete=models.CASCADE, related_name="items"
    )
    type_of_jewellery = models.CharField(max_length=128, blank=True, null=True)
    number_of_articles = models.PositiveIntegerField(default=1)
    purity = models.CharField(max_length=64, blank=True, null=True)
    gross_weight = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    stone_weight = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    net_weight = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    impurity_deducted = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    net_adjusted_weight = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    percent_of_gold = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    actual_gold_rate = models.DecimalField(max_digits=16, decimal_places=3, blank=True, null=True)
    gross_value = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    net_value = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    net_adjusted_value = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    front_image_url = models.URLField(max_length=500, blank=True, null=True)
    back_image_url = models.URLField(max_length=500, blank=True, null=True)
    weighing_machine_image_url = models.URLField(max_length=500, blank=True, null=True)
    appraiser_certificate_image_url = models.URLField(max_length=500, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Jewellery {self.type_of_jewellery} ({self.id})"


class BankDetailsV2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        ApplicationV2, on_delete=models.CASCADE, related_name="bank_details"
    )
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=64, blank=True, null=True)
    customer_name_as_per_bank = models.CharField(max_length=255, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    cheque_image_url = models.URLField(max_length=500, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class AdditionalDetailsV2(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.OneToOneField(
        ApplicationV2, on_delete=models.CASCADE, related_name="additional_details"
    )
    is_employee = models.BooleanField(default=False)
    nominee_relation = models.CharField(max_length=128, blank=True, null=True)
    nominee_full_name = models.CharField(max_length=255, blank=True, null=True)
    nominee_contact_number = models.CharField(max_length=20, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class BankBranch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    branch_name = models.CharField(max_length=255, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    branch_code = models.CharField(max_length=64, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    correct_district = models.CharField(max_length=255, blank=True, null=True)
    sol_id = models.CharField(max_length=64, blank=True, null=True)
    glo_id = models.CharField(max_length=64, blank=True, null=True)
    glo_name = models.CharField(max_length=255, blank=True, null=True)
    agent_id = models.CharField(max_length=64, blank=True, null=True)
    agent_name = models.CharField(max_length=255, blank=True, null=True)
    agent_wise_status = models.CharField(max_length=255, blank=True, null=True)
    zone = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bank_name} - {self.branch_name}"


class PincodeMaster(models.Model):
    pincode = models.CharField(primary_key=True, max_length=10)
    district = models.CharField(max_length=255, blank=True, null=True)
    statename = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=64, blank=True, null=True)
    longitude = models.CharField(max_length=64, blank=True, null=True)
    circlename = models.CharField(max_length=255, blank=True, null=True)
    regionname = models.CharField(max_length=255, blank=True, null=True)
    divisionname = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pincode


class LendingPartnerMaster(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=255)
    available_for = models.CharField(max_length=64, choices=ProductSubCategory.choices)
    available_for_lead_type = models.JSONField(
        default=list,
        blank=True,
        help_text="Lead types for which the lending partner is available",
    )
    bank_rate = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("bank_name", "available_for")

    def __str__(self):
        return f"{self.bank_name} - {self.available_for}"


class DailyGoldRateBank(models.TextChoices):
    AXIS_BANK = "AXIS_BANK", "Axis Bank"


class DailyGoldRateProductType(models.TextChoices):
    GENERAL_PURPOSE = "GENERAL_PURPOSE", "General Purpose"
    MSME = "MSME", "MSME"
    AGRI_ALLIED = "AGRI_ALLIED", "Agri Allied"


class DailyGoldRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_type = models.CharField(
        max_length=128,
        choices=DailyGoldRateProductType.choices,
        default=DailyGoldRateProductType.GENERAL_PURPOSE,
        db_index=True,
        help_text="Product type associated with the gold rate",
    )
    carat = models.CharField(max_length=10, help_text="Gold purity, e.g. 24K, 22K, 18K")
    gold_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Gold rate per gram in INR")
    bank = models.CharField(
        max_length=64,
        choices=DailyGoldRateBank.choices,
        default=DailyGoldRateBank.AXIS_BANK,
        help_text="Bank associated with the gold rate",
    )
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ("product_type", "carat", "bank")
        ordering = ["product_type", "carat", "bank"]

    def __str__(self):
        return f"{self.product_type} | {self.carat} | {self.bank} | ₹{self.gold_rate}"





class WebhookEvent(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Received"
        QUEUED = "QUEUED", "Queued"
        PROCESSED = "PROCESSED", "Processed"
        FAILED = "FAILED", "Failed"

    class Purpose(models.TextChoices):
        PRESCREEN = "PRESCREEN", "Pre-screen"
        LOAN_CREATION = "LOAN_CREATION", "Loan Creation"
        FUND_REFUND = "FUND_REFUND", "Fund Refund"
        UNKNOWN = "UNKNOWN", "Unknown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_id = models.CharField(max_length=128)
    request_id = models.CharField(max_length=128, blank=True, null=True)
    payload = models.JSONField(default=default_json, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RECEIVED)
    purpose = models.CharField(max_length=32, choices=Purpose.choices, default=Purpose.UNKNOWN)
    last_error = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    next_retry_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["application_id"]),
            models.Index(fields=["request_id"]),
            models.Index(fields=["status", "next_retry_at"]),
        ]

    def __str__(self):
        return f"{self.application_id} | {self.status}"


class SaasRequestLog(models.Model):
    class RequestType(models.TextChoices):
        CREATE_LEAD = "CREATE_LEAD", "Create Lead"
        CREATE_LOAN = "CREATE_LOAN", "Create Loan"
        BUREAU_CHECK = "BUREAU_CHECK", "Bureau Check"
        FUND_REFUND = "FUND_REFUND", "Fund Refund"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        ApplicationV2,
        on_delete=models.CASCADE,
        related_name="saas_logs",
        null=True,
        blank=True,
    )
    application_identifier = models.CharField(max_length=128)
    request_type = models.CharField(max_length=32, choices=RequestType.choices)
    attempts = models.PositiveIntegerField(default=0)
    last_payload = models.JSONField(default=default_json, blank=True)
    last_response_status = models.IntegerField(blank=True, null=True)
    last_response_body = models.JSONField(default=default_json, blank=True)
    last_error = models.TextField(blank=True, null=True)
    first_attempt_at = models.DateTimeField(blank=True, null=True)
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("application_identifier", "request_type")
        indexes = [
            models.Index(fields=["application_identifier", "request_type"]),
            models.Index(fields=["last_attempt_at"]),
        ]

    def __str__(self):
        return f"{self.application_id} | {self.request_type}"


class BankLeadTrace(models.Model):
    class Status(models.TextChoices):
        INITIATED = "INITIATED", "Initiated"
        VALIDATION_FAILED = "VALIDATION_FAILED", "Validation Failed"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REJECTED = "REJECTED", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(
        LeadV2,
        on_delete=models.SET_NULL,
        related_name="bank_lead_traces",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="bank_lead_traces",
        null=True,
        blank=True,
    )
    bank_name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    lead_type = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    crm_type = models.CharField(max_length=32, blank=True, null=True, db_index=True)
    bank_api_url = models.URLField(max_length=2048, blank=True, null=True)
    request_headers = models.JSONField(default=default_json, blank=True)
    request_payload = models.JSONField(default=default_json, blank=True)
    response_payload = models.JSONField(default=default_json, blank=True)
    response_status_code = models.IntegerField(blank=True, null=True)
    bank_lead_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.INITIATED, db_index=True)
    error_message = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["bank_name", "created_at"]),
            models.Index(fields=["contact_number", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.bank_name or 'Bank'} | {self.contact_number or '-'} | {self.status}"


class LoanPunchV2(models.Model):
    class ApprovalStatus(models.TextChoices):
        APPROVED = "APPROVED", "Loan Status Updated"
        REJECTED = "REJECTED", "Rejected"
        CHANGE_BANK = "CHANGE_BANK", "Change Bank"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        ApplicationV2, on_delete=models.CASCADE, related_name="punched_loans"
    )
    approval_status = models.CharField(
        max_length=32, choices=ApprovalStatus.choices, default=ApprovalStatus.APPROVED
    )
    bank_name = models.CharField(max_length=255)
    crm_id = models.CharField(max_length=128, blank=True, null=True)
    is_agriculture = models.BooleanField(default=False)
    loan_account_number = models.CharField(max_length=64, blank=True, null=True, unique=True)
    loan_account_document = models.URLField(max_length=2048, blank=True, null=True)
    product_approval_screenshot = models.URLField(max_length=2048, blank=True, null=True)
    loan_opening_date = models.DateField(blank=True, null=True)
    sanctioned_amount = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    approved_tenure = models.PositiveIntegerField(blank=True, null=True)
    disbursed_amount = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    rate_of_interest = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    gross_weight = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    net_weight = models.DecimalField(max_digits=14, decimal_places=3, blank=True, null=True)
    is_customer_kit_gifted = models.BooleanField(default=False)
    is_bank_changed = models.BooleanField(default=False)
    new_bank_name = models.CharField(max_length=255, blank=True, null=True)
    new_bank_state = models.CharField(max_length=255, blank=True, null=True)
    new_bank_district = models.CharField(max_length=255, blank=True, null=True)
    new_bank_branch = models.CharField(max_length=255, blank=True, null=True)
    rejection_reason = models.CharField(max_length=255, blank=True, null=True)
    agent_id = models.CharField(max_length=128, blank=True, null=True)
    agent_name = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan {self.loan_account_number} for {self.application.application_id}"


class LeadAutoClosureSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead_type = models.CharField(max_length=32, choices=LeadType.choices)
    product_subcategory = models.CharField(max_length=64, choices=ProductSubCategory.choices)
    auto_closure_days = models.PositiveIntegerField(default=7)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("lead_type", "product_subcategory")

    def __str__(self):
        return f"{self.lead_type} - {self.product_subcategory} ({self.auto_closure_days} days)"


class ThirdPartyLender(models.Model):
    bank_name = models.CharField(max_length=255)
    ifsc_code = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{4}0[A-Z0-9]{6}$",
                message="Enter a valid IFSC code (e.g., SBIN0001234)",
            )
        ],
    )
    branch = models.CharField(max_length=255)

    class Meta:
        unique_together = ("bank_name", "ifsc_code")
        verbose_name = "Third Party Lender"
        verbose_name_plural = "Third Party Lenders"

    def __str__(self):
        return f"{self.bank_name} - {self.ifsc_code} ({self.branch})"


class CustomerBankAccount(models.Model):
    bank_name = models.CharField(max_length=255)
    ifsc_code = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{4}0[A-Z0-9]{6}$",
                message="Enter a valid IFSC code (e.g., SBIN0001234)",
            )
        ],
    )
    branch = models.CharField(max_length=255)

    class Meta:
        unique_together = ("bank_name", "ifsc_code")
        verbose_name = "Customer Bank Account"
        verbose_name_plural = "Customer Bank Accounts"

    def __str__(self):
        return f"{self.bank_name} - {self.ifsc_code} ({self.branch})"


class RoiConfigurationLeadType(models.TextChoices):
    FRESH = "FRESH", "Fresh"
    BALANCE_TRANSFER = "BALANCE_TRANSFER", "Balance Transfer"
    CO_LENDING = "CO_LENDING", "Co-Lending"
    SELF_LENDING = "SELF_LENDING", "Self Lending"


class RoiConfigurationBank(models.TextChoices):
    AXIS_BANK = "AXIS_BANK", "Axis Bank"
    SIMPLEPAY = "SIMPLEPAY", "Simplepay"


class RoiConfigurationProductType(models.TextChoices):
    GENERAL_PURPOSE = "GENERAL_PURPOSE", "General Purpose"
    MSME = "MSME", "MSME"
    AGRI_ALLIED = "AGRI_ALLIED", "Agri Allied"


class RoiConfigurationTenure(models.TextChoices):
    T_3_MONTHS = "3_MONTHS", "3 months"
    T_6_MONTHS = "6_MONTHS", "6 months"
    T_9_MONTHS = "9_MONTHS", "9 months"
    T_12_MONTHS = "12_MONTHS", "12 months"


class RoiConfigurationRepayment(models.TextChoices):
    BULLET = "BULLET", "Bullet"
    QUARTERLY = "QUARTERLY", "Quarterly"
    MONTHLY = "MONTHLY", "Monthly"
    NA = "NA", "NA"


class RoiConfigurationLoanRange(models.TextChoices):
    LESS_THAN_2_5_LAKHS = "LESS_THAN_2_5_LAKHS", "Less than 2.5 lakhs (<2.5 lakhs)"
    MORE_THAN_2_5_LAKHS = "MORE_THAN_2_5_LAKHS", "More than 2.5 lakhs (>2.5 lakhs)"


class RoiConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead_type = models.CharField(
        max_length=64,
        choices=RoiConfigurationLeadType.choices,
        default=RoiConfigurationLeadType.CO_LENDING,
        help_text="Type of Lead",
    )
    bank = models.CharField(
        max_length=64,
        choices=RoiConfigurationBank.choices,
        default=RoiConfigurationBank.AXIS_BANK,
        help_text="Bank selection",
    )
    product_type = models.CharField(
        max_length=64,
        choices=RoiConfigurationProductType.choices,
        default=RoiConfigurationProductType.GENERAL_PURPOSE,
        help_text="Type of Product",
    )
    tenure = models.CharField(
        max_length=64,
        choices=RoiConfigurationTenure.choices,
        default=RoiConfigurationTenure.T_6_MONTHS,
        help_text="Tenure",
    )
    repayment_schedule = models.CharField(
        max_length=64,
        choices=RoiConfigurationRepayment.choices,
        default=RoiConfigurationRepayment.BULLET,
        help_text="Repayment schedule",
    )
    loan_range = models.CharField(
        max_length=64,
        choices=RoiConfigurationLoanRange.choices,
        default=RoiConfigurationLoanRange.LESS_THAN_2_5_LAKHS,
        help_text="Loan range",
    )
    bank_roi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Bank ROI percentage",
    )
    manipal_roi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Manipal ROI percentage",
    )
    blended_roi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Blended ROI percentage",
    )
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("lead_type", "bank", "product_type", "tenure", "repayment_schedule", "loan_range")
        ordering = ["lead_type", "bank", "product_type", "tenure", "repayment_schedule", "loan_range"]

    def save(self, *args, **kwargs):
        from decimal import Decimal
        if self.bank_roi is not None and self.manipal_roi is not None:
            self.blended_roi = (self.bank_roi * Decimal("0.8")) + (self.manipal_roi * Decimal("0.2"))
        elif self.bank_roi is not None:
            self.blended_roi = self.bank_roi
        else:
            self.blended_roi = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lead_type} | {self.bank} | {self.product_type} | {self.tenure} | {self.repayment_schedule} | {self.loan_range}"


class Customers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.CharField(max_length=100, unique=True, db_index=True, blank=True, null=True)
    fl_id = models.CharField(max_length=100, unique=True, db_index=True, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True, db_index=True)
    is_defaulter = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Customers"
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        identifier = self.customer_id or self.fl_id or self.id
        return f"{self.name or ''} ({identifier})"


class Banner(models.Model):
    """
    Stores banner records with an uploaded image URL, title, and message.
    Used by the web admin to push banners to the mobile app.
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_url = models.URLField(max_length=2048, help_text="Publicly accessible URL of the banner image")
    title = models.CharField(max_length=255, help_text="Banner title")
    message = models.TextField(help_text="Banner message body")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        help_text="Current status of the banner",
    )
    is_active = models.BooleanField(default=True, db_index=True, help_text="Whether the banner is currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Banner"
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.is_active:
            self.status = self.Status.ACTIVE
        else:
            self.status = self.Status.INACTIVE
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({'active' if self.is_active else 'inactive'})"


class ProductV2AvailableFor(models.TextChoices):
    CO_LENDING = "CO_LENDING", "Co-Lending"
    SELF_LENDING = "SELF_LENDING", "Self-Lending"


class ProductV2Category(models.TextChoices):
    CONSUMPTION_LOAN = "CONSUMPTION_LOAN", "Consumption Loan"
    INCOME_LOAN = "INCOME_LOAN", "Income Loan"


class ProductV2RepaymentFrequency(models.TextChoices):
    BULLET = "BULLET", "Bullet"
    QUARTERLY = "QUARTERLY", "Quarterly"
    MONTHLY = "MONTHLY", "Monthly"


class ProductV2Tenure(models.IntegerChoices):
    THREE_MONTHS = 3, "3 months"
    FOUR_MONTHS = 4, "4 months"
    SIX_MONTHS = 6, "6 months"
    NINE_MONTHS = 9, "9 months"
    TWELVE_MONTHS = 12, "12 months"


class ProductV2(models.Model):
    """Product master used by the onboarding v2 product-selection flow."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    available_for = models.JSONField(
        default=list,
        blank=True,
        help_text="Lead types for which the product is available",
    )
    category = models.CharField(
        max_length=64,
        choices=ProductV2Category.choices,
    )
    product_code = models.CharField(max_length=32, unique=True, db_index=True)
    repayment_frequency = models.CharField(
        max_length=32,
        choices=ProductV2RepaymentFrequency.choices,
    )
    tenure_months = models.PositiveSmallIntegerField(
        choices=ProductV2Tenure.choices,
    )
    ltv = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        help_text="LTV percentage, e.g. 80.0000 means 80%",
    )
    minimum_ticket_size = models.DecimalField(max_digits=14, decimal_places=2)
    maximum_ticket_size = models.DecimalField(max_digits=14, decimal_places=2)
    interest_rate = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        help_text="Annual interest percentage",
    )
    processing_fees = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        help_text="Processing fee percentage",
    )
    processing_fees_with_cbo_approval = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        help_text="Processing fee percentage with CBO approval",
    )
    monthly_penalty_on_principal_outstanding = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        help_text="Monthly penalty percentage on outstanding principal",
    )
    non_release_penalty = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        help_text="Penalty percentage when gold is not released within 7 days",
    )
    foreclosure_charges = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        help_text="Foreclosure charge percentage within 30 days",
    )
    stamp_duty = models.CharField(max_length=255)
    source_effective_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    metadata = models.JSONField(default=default_json, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ProductV2"
        verbose_name = "Product V2"
        verbose_name_plural = "Products V2"
        ordering = ["category", "repayment_frequency", "tenure_months", "product_code"]

    def __str__(self):
        return f"{self.product_code} - {self.category}"
