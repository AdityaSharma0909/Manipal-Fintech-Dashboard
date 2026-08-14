from decimal import Decimal
import re
from datetime import timedelta

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from onboarding_v2.models import (
    ApplicationStageSnapshot,
    ApplicationV2,
    CorrectionOnboarding,
    LeadAutoClosureSetting,
    LendingPartnerMaster,
    LeadV2,
    PincodeMaster,
    ProductV2,
)
from onboarding_v2.constants import (
    ApplicationStatus,
    ApplicationStage,
    DocumentStatus,
    DocumentType,
    AddressType,
    Profession,
    ProofOfAddress,
    Religion,
    Category,
    MaritalStatus,
    Relation,
    Gender,
    Qualification,
    LivingWith,
    EmiType,
    InterestType,
    RepaymentFrequency,
    CategoryType,
    DisbursementType,
    Purity,
    TENURE_MONTHS,
    ProductSubCategory,
    JewelleryType,
    PrimaryBorrowerType,
    NriStatus,
    LeadType,
    LeadSource,
    LeadStatus,
    Occupation,
    IncomeSource,
    LoanSubCategory,
    LendingPartner,
    RentalIncome,
    AnnualIncomeFamilyRange,
    HouseOwnership,
    PaymentMode,
    FundTransferredBy,
    TransactionStatus,
)
from onboarding_v2.helpers.fund_refund_helpers import calculate_fund_refund_amounts
from rest_framework import serializers as drf_serializers
from users.models import User
from utils.constants import ROLES


BT_LEAD_SO_MIN_TENURE_DAYS = 60


def _phone_lookup_values(phone):
    values = []

    def add(value):
        if value is None:
            return
        value = str(value).strip()
        if value and value not in values:
            values.append(value)

    add(phone)

    digits = re.sub(r"\D", "", str(phone or ""))
    if not digits:
        return values

    add(digits)
    if len(digits) == 10:
        add(f"+91{digits}")
        add(f"91{digits}")
    elif digits.startswith("91") and len(digits) == 12:
        add(digits[2:])
        add(f"+{digits}")
    elif digits.startswith("0") and len(digits) == 11:
        national_digits = digits[1:]
        add(national_digits)
        add(f"+91{national_digits}")
        add(f"91{national_digits}")

    return values


def _user_exists_for_contact_number(contact_number):
    lookup = None
    for phone in _phone_lookup_values(contact_number):
        lookup = Q(phone=phone) if lookup is None else lookup | Q(phone=phone)

    digits = re.sub(r"\D", "", str(contact_number or ""))
    national_digits = None
    if len(digits) == 10:
        national_digits = digits
    elif digits.startswith("91") and len(digits) == 12:
        national_digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11:
        national_digits = digits[1:]

    if national_digits:
        suffix_lookup = Q(phone__endswith=national_digits)
        lookup = suffix_lookup if lookup is None else lookup | suffix_lookup

    return bool(lookup and User.objects.filter(lookup).exists())


class LeadTypeChoiceField(serializers.ChoiceField):
    LEGACY_VALUE_MAP = {
        "BT": LeadType.BALANCE_TRANSFER,
    }

    def to_internal_value(self, data):
        if isinstance(data, str):
            normalized = data.strip().upper().replace(" ", "_").replace("-", "_")
            data = self.LEGACY_VALUE_MAP.get(normalized, normalized)
        return super().to_internal_value(data)

    def to_representation(self, value):
        if isinstance(value, str) and value.strip().upper() == "BT":
            value = LeadType.BALANCE_TRANSFER
        return super().to_representation(value)


class LeadSourceChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            normalized = data.strip().upper().replace(" ", "_").replace("-", "_")
            return super().to_internal_value(normalized)
        return super().to_internal_value(data)


def _normalize_lending_partner_value(value):
    return re.sub(r"[\s_-]+", "", (value or "").strip().lower())


def canonicalize_lending_partner_value(value, available_for=None):
    if value in (None, ""):
        return value

    partner_qs = LendingPartnerMaster.objects.filter(bank_name__iexact=value)
    if available_for:
        partner_qs = partner_qs.filter(available_for=available_for)

    canonical_partner = partner_qs.order_by("bank_name").first()
    if canonical_partner:
        return canonical_partner.bank_name

    normalized_value = _normalize_lending_partner_value(value)
    partner_qs = LendingPartnerMaster.objects.all()
    if available_for:
        partner_qs = partner_qs.filter(available_for=available_for)

    normalized_matches = [
        partner
        for partner in partner_qs
        if _normalize_lending_partner_value(partner.bank_name) == normalized_value
    ]
    if len(normalized_matches) == 1:
        return normalized_matches[0].bank_name
    if len(normalized_matches) > 1:
        raise serializers.ValidationError(
            f'"{value}" matches multiple configured lending partners for {available_for or "this application"}.'
        )

    valid_values = {choice[0] for choice in LendingPartner.choices}
    valid_labels = {choice[1] for choice in LendingPartner.choices}
    if value in valid_values or value in valid_labels:
        return value

    if available_for:
        raise serializers.ValidationError(
            f'"{value}" is not configured for {available_for}.'
        )
    raise serializers.ValidationError(f'"{value}" is not a valid choice.')


class LeadV2Serializer(serializers.ModelSerializer):
    class Meta:
        model = LeadV2
        fields = "__all__"


class ApplicationV2Serializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lead_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    customer_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contact_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pan_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pincode = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, allow_null=True)
    dob = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Fields returned by get detail API
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lead_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lead_added_on = serializers.DateTimeField(required=False, allow_null=True)
    requested_amount = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, allow_null=True)
    dob_from_pan = serializers.DateField(required=False, allow_null=True)
    place_of_birth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    alternate_no = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    father_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mother_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    marital_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profession = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    occupation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profile_pic = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    income_source = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    annual_income = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    net_income_per_month = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    net_worth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    religion = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    category = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    isFreshOnboardingSubmitted = serializers.SerializerMethodField()
    punched_by_name = serializers.CharField(source="punched_by.get_full_name", read_only=True)
    assigned_rh_name = serializers.CharField(source="assigned_rh.get_full_name", read_only=True)

    class Meta:
        model = ApplicationV2
        fields = [f.name for f in ApplicationV2._meta.fields] + [
            "customer_id",
            "lead_code",
            "email_address",
            "customer_name",
            "contact_number",
            "pan_number",
            "pincode",
            "amount",
            "dob",
            "gender",
            "address",
            # New detail fields
            "name",
            "email",
            "phone_no",
            "lead_id",
            "lead_added_on",
            "requested_amount",
            "dob_from_pan",
            "place_of_birth",
            "alternate_no",
            "father_name",
            "mother_name",
            "marital_status",
            "profession",
            "occupation",
            "profile_pic",
            "income_source",
            "annual_income",
            "net_income_per_month",
            "net_worth",
            "religion",
            "category",
            "isFreshOnboardingSubmitted",
            "punched_by_name",
            "assigned_rh_name",
        ]

    def get_isFreshOnboardingSubmitted(self, obj):
        return (
            obj.loan_type in [LeadType.FRESH, LeadType.CO_LENDING] and obj.stage == ApplicationStage.SUBMITTED
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Fetch actual values from lead/snapshots to return in response representation
        lead = instance.lead
        if lead:
            ret["name"] = lead.customer_name
            ret["email"] = lead.email_address
            ret["phone_no"] = lead.contact_number
            ret["dob"] = str(lead.dob) if lead.dob else None
            ret["gender"] = lead.gender
            ret["requested_amount"] = str(lead.amount) if lead.amount is not None else None
            ret["customer_id"] = lead.customer_id
            ret["lead_code"] = lead.lead_code
            ret["email_address"] = lead.email_address
            ret["customer_name"] = lead.customer_name
            ret["contact_number"] = lead.contact_number
            ret["pan_number"] = lead.pan_number
            ret["pincode"] = lead.pincode
            ret["amount"] = str(lead.amount) if lead.amount is not None else None
            ret["address"] = lead.address
            ret["lead_id"] = str(lead.id) if lead.id else None
            ret["lead_added_on"] = lead.created_at.isoformat() if lead.created_at else None

        # Fetch basic snapshot values
        try:
            basic_snap = instance.stage_snapshots.get(stage="BASIC")
            basic = basic_snap.payload if isinstance(basic_snap.payload, dict) else {}
        except Exception:
            # Fallback to stage_payload
            try:
                basic = instance.stage_payload.get("basic", {}) if isinstance(instance.stage_payload, dict) else {}
            except Exception:
                basic = {}
            
        ret["place_of_birth"] = basic.get("place_of_birth")
        ret["alternate_no"] = basic.get("alternate_no") or basic.get("alternate_number")
        ret["father_name"] = basic.get("father_name") or basic.get("fathers_name")
        ret["mother_name"] = basic.get("mother_name") or basic.get("mothers_name")
        ret["marital_status"] = basic.get("marital_status")
        ret["profession"] = basic.get("profession") or instance.applicant_profession
        ret["occupation"] = basic.get("occupation") or instance.occupation
        ret["income_source"] = basic.get("income_source") or instance.income_source
        ret["annual_income"] = basic.get("annual_income") or basic.get("annual_income_family")
        ret["net_income_per_month"] = basic.get("net_income_per_month") or basic.get("monthly_income")
        ret["net_worth"] = basic.get("net_worth")
        ret["religion"] = basic.get("religion")
        ret["category"] = basic.get("category") or instance.caste

        # Fetch PAN snapshot values
        try:
            pan_snap = instance.stage_snapshots.get(stage="PAN")
            pan = pan_snap.payload if isinstance(pan_snap.payload, dict) else {}
        except Exception:
            try:
                pan = instance.stage_payload.get("pan", {}) if isinstance(instance.stage_payload, dict) else {}
            except Exception:
                pan = {}
        ret["dob_from_pan"] = pan.get("dob_from_pan") or pan.get("dob_as_per_pan")

        # Fetch SELFIE snapshot values
        try:
            selfie_snap = instance.stage_snapshots.get(stage="SELFIE")
            selfie = selfie_snap.payload if isinstance(selfie_snap.payload, dict) else {}
        except Exception:
            try:
                selfie = instance.stage_payload.get("selfie", {}) if isinstance(instance.stage_payload, dict) else {}
            except Exception:
                selfie = {}
        ret["profile_pic"] = selfie.get("file_url") or selfie.get("image_url")

        return ret

    def update(self, instance, validated_data):
        lead = instance.lead
        lead_updated = False

        # Support name mapping
        name_val = validated_data.pop("name", None) or validated_data.pop("customer_name", None)
        if name_val is not None and lead:
            lead.customer_name = name_val
            lead_updated = True

        # Support email mapping
        email_val = validated_data.pop("email", None) or validated_data.pop("email_address", None)
        if email_val is not None and lead:
            lead.email_address = email_val
            lead_updated = True

        # Support phone mapping
        phone_no_val = validated_data.pop("phone_no", None) or validated_data.pop("contact_number", None)
        if phone_no_val is not None and lead:
            lead.contact_number = phone_no_val
            lead_updated = True

        # Support DOB mapping
        dob_val = validated_data.pop("dob", None)
        if dob_val is not None and lead:
            lead.dob = dob_val
            lead_updated = True

        # Support gender mapping
        gender_val = validated_data.pop("gender", None)
        if gender_val is not None and lead:
            lead.gender = gender_val
            lead_updated = True

        # Support amount mapping
        req_amt_val = validated_data.pop("requested_amount", None) or validated_data.pop("amount", None)
        if req_amt_val is not None and lead:
            lead.amount = req_amt_val
            lead_updated = True

        # Other lead updates
        validated_data.pop("lead_id", None)
        
        lead_added_on_val = validated_data.pop("lead_added_on", None)
        if lead_added_on_val is not None and lead:
            lead.created_at = lead_added_on_val
            lead_updated = True

        cust_id_val = validated_data.pop("customer_id", None)
        if cust_id_val is not None and lead:
            lead.customer_id = cust_id_val
            lead_updated = True

        lead_code_val = validated_data.pop("lead_code", None)
        if lead_code_val is not None and lead:
            lead.lead_code = lead_code_val
            lead_updated = True

        pincode_val = validated_data.pop("pincode", None)
        if pincode_val is not None and lead:
            lead.pincode = pincode_val
            lead_updated = True

        pan_number_val = validated_data.pop("pan_number", None)
        if pan_number_val is not None and lead:
            lead.pan_number = pan_number_val
            lead_updated = True

        address_val = validated_data.pop("address", None)
        if address_val is not None and lead:
            lead.address = address_val
            lead_updated = True

        if lead_updated:
            lead.save()

        # Update model fields on ApplicationV2
        profession_val = validated_data.get("profession")
        if profession_val is not None:
            instance.applicant_profession = profession_val

        occupation_val = validated_data.get("occupation")
        if occupation_val is not None:
            instance.occupation = occupation_val

        income_src_val = validated_data.get("income_source")
        if income_src_val is not None:
            instance.income_source = income_src_val

        category_val = validated_data.get("category")
        if category_val is not None:
            instance.caste = category_val

        # Helper to update snapshots AND stage_payload on application
        def update_snapshot_and_payload(stage_name, fields_dict):
            if not fields_dict:
                return
            
            # 1. Update stage_snapshots
            snapshot, _ = instance.stage_snapshots.get_or_create(
                stage=stage_name,
                defaults={"payload": {}, "is_complete": False}
            )
            payload = snapshot.payload if isinstance(snapshot.payload, dict) else {}
            for k, v in fields_dict.items():
                if v is not None:
                    payload[k] = v
            snapshot.payload = payload
            snapshot.save()

            # 2. Update stage_payload on application
            stage_key = stage_name.lower()
            current_stage_payload = instance.stage_payload if isinstance(instance.stage_payload, dict) else {}
            stage_payload_data = current_stage_payload.get(stage_key) or {}
            if not isinstance(stage_payload_data, dict):
                stage_payload_data = {}
            for k, v in fields_dict.items():
                if v is not None:
                    stage_payload_data[k] = v
            current_stage_payload[stage_key] = stage_payload_data
            instance.stage_payload = current_stage_payload

        # BASIC snapshot payload updates
        basic_fields = {}
        for f in ["place_of_birth", "alternate_no", "father_name", "mother_name", "marital_status", "profession", "occupation", "income_source", "annual_income", "net_income_per_month", "net_worth", "religion", "category"]:
            val = validated_data.pop(f, None)
            if val is not None:
                basic_fields[f] = val
        update_snapshot_and_payload("BASIC", basic_fields)

        # PAN snapshot payload updates
        pan_fields = {}
        dob_pan = validated_data.pop("dob_from_pan", None)
        if dob_pan is not None:
            pan_fields["dob_from_pan"] = str(dob_pan)
            pan_fields["dob_as_per_pan"] = str(dob_pan)
            pan_fields["dob"] = str(dob_pan)
        update_snapshot_and_payload("PAN", pan_fields)

        # SELFIE snapshot payload updates
        selfie_fields = {}
        profile_pic_val = validated_data.pop("profile_pic", None)
        if profile_pic_val is not None:
            selfie_fields["file_url"] = profile_pic_val
            selfie_fields["image_url"] = profile_pic_val
            selfie_fields["selfie_url"] = profile_pic_val
        update_snapshot_and_payload("SELFIE", selfie_fields)

        # Update remaining fields of ApplicationV2
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ApplicationListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="lead.customer_name")
    date = serializers.DateTimeField(source="created_at")
    customer_id = serializers.CharField(source="lead.customer_id")
    lead_code = serializers.CharField(source="lead.lead_code", allow_null=True)
    application_id = serializers.CharField()
    status = serializers.CharField()
    amount = serializers.SerializerMethodField()
    disbursed_amount = serializers.SerializerMethodField()
    loan_type = serializers.CharField(allow_null=True)
    mobile_number = serializers.CharField(source="lead.contact_number")
    email_address = serializers.CharField(source="lead.email_address", allow_null=True)
    product_category = serializers.CharField(source="lead.product_category")
    product_subcategory = serializers.CharField(source="lead.product_subcategory", allow_null=True)
    lead_type = serializers.CharField(source="lead.lead_type", allow_null=True)
    pincode = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    bank_branch = serializers.SerializerMethodField()
    prescreen_submitted = serializers.SerializerMethodField()
    isFreshOnboardingSubmitted = serializers.SerializerMethodField()
    lending_partner = serializers.CharField()
    punched_by_name = serializers.CharField(source="punched_by.get_full_name", read_only=True)
    assigned_rh_name = serializers.CharField(source="assigned_rh.get_full_name", read_only=True)

    class Meta:
        model = ApplicationV2
        fields = [
            "name",
            "date",
            "customer_id",
            "lead_code",
            "application_id",
            "status",
            "van_number",
            "amount",
            "disbursed_amount",
            "loan_type",
            "mobile_number",
            "email_address",
            "product_category",
            "product_subcategory",
            "lead_type",
            "pincode",
            "state",
            "district",
            "bank_branch",
            "prescreen_submitted",
            "isFreshOnboardingSubmitted",
            "lending_partner",
            "parent_application_id",
            "rh_remarks",
            "rh_rejection_reason",
            "punched_by",
            "punched_by_name",
            "assigned_rh",
            "assigned_rh_name",
        ]

    def get_amount(self, obj):
        # Check for LOAN stage snapshot first
        snapshots = getattr(obj, "stage_snapshots", None)
        loan_payload = {}
        if snapshots is not None:
            # If prefetched
            for snapshot in snapshots.all():
                if snapshot.stage == ApplicationStage.LOAN:
                    loan_payload = snapshot.payload
                    break
        else:
            try:
                snapshot = obj.stage_snapshots.get(stage=ApplicationStage.LOAN)
                loan_payload = snapshot.payload
            except ApplicationStageSnapshot.DoesNotExist:
                pass
        
        if loan_payload and isinstance(loan_payload, dict):
            # Prioritize Required BT amount for BT flows
            bt_amount = loan_payload.get("requested_amount") or loan_payload.get("required_bt_amount")
            if bt_amount:
                try:
                    return str(Decimal(str(bt_amount)).quantize(Decimal("0.01")))
                except Exception:
                    pass
        
        # Fallback to lead.amount
        if obj.lead.amount:
            return str(obj.lead.amount.quantize(Decimal("0.01")))
        return None

    def get_disbursed_amount(self, obj):
        amounts = [
            loan.disbursed_amount
            for loan in obj.punched_loans.all()
            if loan.disbursed_amount is not None
        ]
        if not amounts:
            return None
        return str(sum(amounts, Decimal("0.00")).quantize(Decimal("0.01")))

    def _get_address_payload(self, obj):
        snapshots = getattr(obj, "stage_snapshots", None)
        if snapshots is not None:
            for snapshot in snapshots.all():
                if snapshot.stage == ApplicationStage.ADDRESS:
                    payload = snapshot.payload
                    return payload if isinstance(payload, dict) else {}
        try:
            snapshot = obj.stage_snapshots.get(stage=ApplicationStage.ADDRESS)
            payload = snapshot.payload
            return payload if isinstance(payload, dict) else {}
        except ApplicationStageSnapshot.DoesNotExist:
            return {}

    def _resolve_address_pincode(self, obj):
        payload = self._get_address_payload(obj)
        permanent = payload.get("permanent") if isinstance(payload.get("permanent"), dict) else {}
        current = payload.get("current") if isinstance(payload.get("current"), dict) else {}
        return permanent.get("pincode") or current.get("pincode")

    def _get_pincode_record(self, obj):
        pincode = self._resolve_address_pincode(obj)
        if not pincode:
            return None
        cache = self.context.setdefault("pincode_cache", {})
        if pincode in cache:
            return cache[pincode]
        try:
            record = PincodeMaster.objects.get(pincode=pincode)
        except PincodeMaster.DoesNotExist:
            record = None
        cache[pincode] = record
        return record

    def get_pincode(self, obj):
        return self._resolve_address_pincode(obj)

    def get_state(self, obj):
        payload = self._get_address_payload(obj)
        permanent = payload.get("permanent") if isinstance(payload.get("permanent"), dict) else {}
        current = payload.get("current") if isinstance(payload.get("current"), dict) else {}
        state = permanent.get("state") or current.get("state")
        if state:
            return state
        record = self._get_pincode_record(obj)
        return record.statename if record else None

    def get_district(self, obj):
        payload = self._get_address_payload(obj)
        permanent = payload.get("permanent") if isinstance(payload.get("permanent"), dict) else {}
        current = payload.get("current") if isinstance(payload.get("current"), dict) else {}
        district = permanent.get("district") or current.get("district")
        if district:
            return district
        record = self._get_pincode_record(obj)
        return record.district if record else None

    def get_bank_branch(self, obj):
        return obj.partner_branch_name or "N/A"

    def get_prescreen_submitted(self, obj):
        return bool(getattr(obj, "saas_request_id", None))

    def get_isFreshOnboardingSubmitted(self, obj):
        return (
            obj.loan_type in [LeadType.FRESH, LeadType.CO_LENDING] and obj.stage == ApplicationStage.SUBMITTED
        )


class ApplicationStageSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStageSnapshot
        fields = "__all__"


class LeadCreateSerializer(serializers.ModelSerializer):
    lead_type = LeadTypeChoiceField(choices=LeadType.choices, required=False, allow_null=True)
    source = LeadSourceChoiceField(choices=LeadSource.choices, required=False, allow_null=True)
    crm_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lending_partner = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    sol_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=64)
    prescreen_submitted = serializers.SerializerMethodField()
    isFreshOnboardingSubmitted = serializers.SerializerMethodField()
    application_id = serializers.SerializerMethodField()
    parent_application_id = serializers.SerializerMethodField()
    _application_cache = None

    class Meta:
        model = LeadV2
        fields = "__all__"
        read_only_fields = ["id", "created_at", "modified_at"]

    def validate_customer_name(self, value):
        if value and len(value.strip()) > 40:
            raise serializers.ValidationError("Full Name should be under 40 characters.")
        return value

    def validate_lending_partner(self, value):
        available_for = self.initial_data.get("product_subcategory")
        if not available_for and self.instance is not None:
            available_for = getattr(self.instance, "product_subcategory", None)
        return canonicalize_lending_partner_value(value, available_for)

    def _validate_bt_creator_eligibility(self, attrs):
        created_by = attrs.get("created_by")
        if not created_by:
            raise serializers.ValidationError({
                "created_by": "Sales Officer is required for Balance Transfer leads."
            })

        if getattr(created_by, "role", None) != ROLES.SALES_OFFICER.value:
            raise serializers.ValidationError({
                "created_by": "Only Sales Officer users can create Balance Transfer leads."
            })

        date_of_joining = getattr(created_by, "date_of_joining", None)
        if not date_of_joining:
            raise serializers.ValidationError({
                "created_by": "Sales Officer date of joining is required for Balance Transfer leads."
            })

        if getattr(created_by, "exclude_from_bt_date_logic", False):
            return

        min_joining_date = timezone.localdate() - timedelta(days=BT_LEAD_SO_MIN_TENURE_DAYS)
        if date_of_joining > min_joining_date:
            raise serializers.ValidationError({
                "created_by": "Sales Officer must have completed 60 days from date of joining to create Balance Transfer leads."
            })

    def validate(self, attrs):
        sol_id = attrs.pop("sol_id", None)
        if sol_id is not None:
            metadata = attrs.get("metadata") or {}
            metadata = dict(metadata) if isinstance(metadata, dict) else {}
            metadata["sol_id"] = str(sol_id).strip()
            attrs["metadata"] = metadata

        contact_number = attrs.get("contact_number")
        product_subcategory = attrs.get("product_subcategory")
        lead_type = attrs.get("lead_type")
        crm_type = attrs.get("crm_type")

        if crm_type in (None, ""):
            attrs["crm_type"] = None
        else:
            crm_type = str(crm_type).strip().upper()
            if crm_type not in {"BALANCE_TRANSFER", "FRESH"}:
                raise serializers.ValidationError({
                    "crm_type": "crm_type must be either BALANCE_TRANSFER or FRESH."
                })
            attrs["crm_type"] = crm_type

        if product_subcategory == ProductSubCategory.GOLD_LOAN and not lead_type:
            raise serializers.ValidationError({"lead_type": "Lead type is required for Gold Loan leads."})

        if lead_type == LeadType.BALANCE_TRANSFER:
            self._validate_bt_creator_eligibility(attrs)

        if contact_number:
            if lead_type != LeadType.BANK_LEAD and product_subcategory != ProductSubCategory.GOLD_LOAN:
                if _user_exists_for_contact_number(contact_number):
                    raise serializers.ValidationError({
                        "contact_number": "A user with this contact number already exists."
                    })

            # FL and BT journeys must not start while the same customer already
            # has a Co-Lending application in progress. The regular Gold Loan
            # duplicate check below is scoped to the requested lead type, so it
            # cannot enforce this cross-type restriction.
            if (
                product_subcategory == ProductSubCategory.GOLD_LOAN
                and lead_type in {LeadType.FRESH, LeadType.BALANCE_TRANSFER}
                and ApplicationV2.objects.filter(
                    lead__contact_number=contact_number,
                    lead__product_subcategory=product_subcategory,
                    lead__lead_type=LeadType.CO_LENDING,
                    status=ApplicationStatus.IN_PROGRESS,
                )
                .exclude(
                    lead__status__in=[
                        LeadStatus.UNVERIFIED,
                        LeadStatus.AUTO_CLOSED,
                    ]
                )
                .exists()
            ):
                raise serializers.ValidationError({
                    "contact_number": (
                        "An in-progress Co-Lending application already exists "
                        "for this contact number."
                    )
                })

            # Check for existing leads with same contact number AND product subcategory
            query = {"contact_number": contact_number}
            # Include product_subcategory in filter even if it's None/missing in attrs
            # as it's a field on the model we want to match against.
            query["product_subcategory"] = product_subcategory

            # For GOLD_LOAN, duplicity check includes Lead Type
            if product_subcategory == ProductSubCategory.GOLD_LOAN:
                query["lead_type"] = lead_type
            
            # Exclude leads with status 'UNVERIFIED' or 'AUTO_CLOSED' from duplicacy check
            # Also exclude BANK_LEADs as they don't count for duplicity according to the user
            existing_leads = (
                LeadV2.objects.filter(**query)
                .exclude(status__in=[LeadStatus.UNVERIFIED, LeadStatus.AUTO_CLOSED])
                .exclude(lead_type=LeadType.BANK_LEAD)
                .prefetch_related("applications")
            )

            for lead in existing_leads:
                # If a lead has no application, it's considered 'in-progress' or 'stuck', so block new lead creation
                subcat_display = product_subcategory or "this product"
                if not lead.applications.exists():
                    raise serializers.ValidationError({"contact_number": f"A lead for {subcat_display} already exists for this contact number."})

                # If a lead has an application, check its status
                latest_app = lead.applications.last()

                if lead_type == LeadType.BALANCE_TRANSFER:
                    bt_blocked_statuses = [
                        ApplicationStatus.IN_PROGRESS,
                        ApplicationStatus.SUBMITTED_TO_UNDERWRITING,
                        ApplicationStatus.ESIGN_INITIATED,
                        ApplicationStatus.ESIGN_COMPLETED,
                        ApplicationStatus.RH_APPROVAL_PENDING,
                        ApplicationStatus.APPROVED_BY_RH,
                        ApplicationStatus.APPROVED_BY_ACCOUNTS,
                        # ApplicationStatus.BT_FUND_DISBURSED,
                    ]
                    if latest_app and latest_app.status in bt_blocked_statuses:
                        raise serializers.ValidationError({
                            "contact_number": f"A Balance Transfer lead with status '{latest_app.get_status_display()}' already exists for this contact number."
                        })
                else:
                    # We block if the application is in a pre-submission state (DRAFT) or sent back for correction.
                    # We also block if it is in PUNCHING_PENDING, as it's not yet fully submitted to the core system.
                    # Only once it's SUBMITTED, LOAN_STATUS_UPDATED or finalized (REJECTED, DROPPED, etc.) do we allow a new lead.
                    blocked_statuses = [
                        ApplicationStatus.DRAFT,
                        ApplicationStatus.CORRECTION,
                        ApplicationStatus.IN_PROGRESS,
                        ApplicationStatus.PUNCHING_PENDING,
                        ApplicationStatus.READY_FOR_LOAN,
                        ApplicationStatus.SENT_FOR_PRE_SCREENING,
                        ApplicationStatus.ALLOCATION_PENDING,
                        ApplicationStatus.COMMERCIAL_PROCESSING,
                        ApplicationStatus.DEVIATION_REQUESTED,
                    ]
                    if latest_app and latest_app.status in blocked_statuses:
                        raise serializers.ValidationError({"contact_number": f"An active {subcat_display} application ({latest_app.status}) exists for this contact number."})

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        metadata = getattr(instance, "metadata", {}) or {}
        data["sol_id"] = metadata.get("sol_id") if isinstance(metadata, dict) else None
        return data

    def get_prescreen_submitted(self, obj):
        app = self._get_application(obj)
        return bool(getattr(app, "saas_request_id", None)) if app else False

    def get_isFreshOnboardingSubmitted(self, obj):
        app = self._get_application(obj)
        return (
            app.loan_type == LeadType.FRESH and app.stage == ApplicationStage.SUBMITTED
        ) if app else False

    def get_application_id(self, obj):
        app = self._get_application(obj)
        return getattr(app, "application_id", None) if app else None

    def get_parent_application_id(self, obj):
        app = self._get_application(obj)
        return getattr(app, "parent_application_id", None) if app else None

    def _get_application(self, obj):
        if self._application_cache is None:
            self._application_cache = {}
        if obj.pk in self._application_cache:
            return self._application_cache[obj.pk]
        apps = getattr(obj, "applications", None)
        if apps is None:
            self._application_cache[obj.pk] = None
            return None
        app = apps.first() if hasattr(apps, "first") else (apps[0] if apps else None)
        self._application_cache[obj.pk] = app
        return app

    def create(self, validated_data):
        state = validated_data.pop("state", None)
        metadata = validated_data.get("metadata") or {}
        m = dict(metadata) if isinstance(metadata, dict) else {}
        if state is not None:
            m["state"] = state
            validated_data["metadata"] = m
        return super().create(validated_data)

    def update(self, instance, validated_data):
        state = validated_data.pop("state", None)
        if state is not None:
            metadata = getattr(instance, "metadata", {}) or {}
            m = dict(metadata) if isinstance(metadata, dict) else {}
            m["state"] = state
            validated_data["metadata"] = m
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        meta = getattr(instance, "metadata", {}) or {}
        data["state"] = meta.get("state")
        # Fallback for leads created before lending_partner was a model field
        if not data.get("lending_partner"):
            data["lending_partner"] = meta.get("lending_partner")
        return data


class LeadV2Serializer(serializers.ModelSerializer):
    prescreen_submitted = serializers.SerializerMethodField()
    isFreshOnboardingSubmitted = serializers.SerializerMethodField()
    application_id = serializers.CharField(read_only=True)
    state = serializers.CharField(source="metadata.state", required=False)

    _application_cache = None

    class Meta:
        model = LeadV2
        fields = [
            "id",
            "customer_id",
            "lead_code",
            "contact_number",
            "email_address",
            "customer_name",
            "product_category",
            "product_subcategory",
            "lead_type",
            "lending_partner",
            "bank",
            "bank_branch",
            "gender",
            "dob",
            "address",
            "pan_number",
            "is_pan_verified",
            "amount",
            "pincode",
            "source",
            "lending_partner",
            "bank",
            "bank_branch",
            "BankLeadID",
            "gender",
            "dob",
            "address",
            "pan_number",
            "is_pan_verified",
            "state",
            "status",
            "parent_lead_code",
            "prescreen_submitted",
            "isFreshOnboardingSubmitted",
            "application_id",
            "assigned_to",
            "created_at",
            "modified_at",
        ]
        # customer_id is set server-side (view) but must be writable here
        read_only_fields = ["id", "created_at", "modified_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Fallback for leads created before lending_partner was a model field
        if not data.get("lending_partner"):
            meta = getattr(instance, "metadata", {}) or {}
            data["lending_partner"] = meta.get("lending_partner")
        return data

    def get_prescreen_submitted(self, obj):
        app = self._get_application(obj)
        return bool(getattr(app, "saas_request_id", None)) if app else False

    def get_isFreshOnboardingSubmitted(self, obj):
        app = self._get_application(obj)
        return (
            app.loan_type == LeadType.FRESH and app.stage == ApplicationStage.SUBMITTED
        ) if app else False

    def get_application_id(self, obj):
        app = self._get_application(obj)
        return getattr(app, "application_id", None) if app else None

    def _get_application(self, obj):
        if self._application_cache is None:
            self._application_cache = {}
        if obj.pk in self._application_cache:
            return self._application_cache[obj.pk]
        apps = getattr(obj, "applications", None)
        if apps is None:
            self._application_cache[obj.pk] = None
            return None
        app = apps.first() if hasattr(apps, "first") else (apps[0] if apps else None)
        self._application_cache[obj.pk] = app
        return app

    def create(self, validated_data):
        state = validated_data.pop("state", None)
        lending_partner = validated_data.pop("lending_partner", None)
        metadata = validated_data.get("metadata") or {}
        m = dict(metadata) if isinstance(metadata, dict) else {}
        if state is not None:
            m["state"] = state
        if lending_partner is not None:
            m["lending_partner"] = lending_partner
        if state is not None or lending_partner is not None:
            validated_data["metadata"] = m
        return super().create(validated_data)

    def update(self, instance, validated_data):
        state = validated_data.pop("state", None)
        lending_partner = validated_data.pop("lending_partner", None)
        if state is not None or lending_partner is not None:
            metadata = getattr(instance, "metadata", {}) or {}
            m = dict(metadata) if isinstance(metadata, dict) else {}
            if state is not None:
                m["state"] = state
            if lending_partner is not None:
                m["lending_partner"] = lending_partner
            validated_data["metadata"] = m
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        meta = getattr(instance, "metadata", {}) or {}
        data["state"] = meta.get("state")
        data["lending_partner"] = meta.get("lending_partner")
        return data


class ApplicationCreateSerializer(serializers.ModelSerializer):
    loan_type = LeadTypeChoiceField(choices=LeadType.choices, required=False, allow_null=True)
    lending_partner = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    punched_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    assigned_rh = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    punched_by_name = serializers.CharField(source="punched_by.get_full_name", read_only=True)
    assigned_rh_name = serializers.CharField(source="assigned_rh.get_full_name", read_only=True)

    class Meta:
        model = ApplicationV2
        fields = [
            "id",
            "application_id",
            "lead",
            "lending_partner",
            "loan_type",
            "status",
            "stage",
            "pre_screen_completion",
            "post_screen_completion",
            "parent_application_id",
            "punched_by",
            "punched_by_name",
            "assigned_rh",
            "assigned_rh_name",
        ]
        # application_id is set server-side in the view; keep only the primary key read-only
        read_only_fields = ["id"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Model fields are already in snake_case
        return data

    def validate_lending_partner(self, value):
        lead = self.initial_data.get("lead")
        lead_obj = None
        if lead:
            lead_obj = LeadV2.objects.filter(pk=lead).first()

        available_for = getattr(lead_obj, "product_subcategory", None)
        return canonicalize_lending_partner_value(value, available_for)


class StageUpdateSerializer(serializers.Serializer):
    stage = serializers.CharField()
    payload = serializers.JSONField()
    is_complete = serializers.BooleanField(default=False)


class SelfDeclarationSerializer(serializers.Serializer):
    consent_given = serializers.BooleanField(required=True)
    otp_verified = serializers.BooleanField(required=True)
    consent_text = serializers.CharField(required=True, allow_blank=False)
    mobile_number = serializers.CharField(required=False, allow_blank=True)
    otp_reference = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    consent_timestamp = serializers.DateTimeField(required=False, allow_null=True)
    consent_ip = serializers.IPAddressField(required=False, allow_null=True)

    def validate(self, attrs):
        if self.context.get("is_complete", False):
            if attrs.get("consent_given") is not True:
                raise serializers.ValidationError(
                    {"consent_given": "Customer consent is required."}
                )
            if attrs.get("otp_verified") is not True:
                raise serializers.ValidationError(
                    {"otp_verified": "Consent OTP must be verified."}
                )

        request = self.context.get("request")
        attrs.setdefault("consent_timestamp", timezone.now())
        if request and not attrs.get("consent_ip"):
            forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
            attrs["consent_ip"] = (
                forwarded_for.split(",", 1)[0].strip()
                or request.META.get("REMOTE_ADDR")
            )
        return attrs


class ChargesDetailsSerializer(serializers.Serializer):
    processing_fee = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False
    )
    stamp_duty = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False
    )
    insurance_charges = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False
    )
    documentation_charges = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False
    )
    other_charges = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False
    )
    total_charges = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False
    )
    net_disbursement_amount = serializers.DecimalField(
        max_digits=16, decimal_places=2, required=False
    )
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    CHARGE_FIELDS = (
        "processing_fee",
        "stamp_duty",
        "insurance_charges",
        "documentation_charges",
        "other_charges",
    )

    def validate(self, attrs):
        application = self.context.get("application")
        for field in self.CHARGE_FIELDS:
            if attrs.get(field) is None and application is not None:
                attrs[field] = Decimal(
                    str(getattr(application, field, None) or Decimal("0"))
                )

        calculated_total = sum(
            (attrs.get(field) or Decimal("0") for field in self.CHARGE_FIELDS),
            Decimal("0"),
        )
        supplied_total = attrs.get("total_charges")
        if supplied_total is not None and supplied_total != calculated_total:
            raise serializers.ValidationError(
                {
                    "total_charges": (
                        "Total charges must equal processing fee, stamp duty, "
                        "insurance, documentation and other charges."
                    )
                }
            )
        attrs["total_charges"] = calculated_total

        if application is not None and attrs.get("net_disbursement_amount") is None:
            requested_amount = getattr(application, "requested_amount", None)
            if requested_amount is None:
                loan_snapshot = application.stage_snapshots.filter(
                    stage=ApplicationStage.LOAN
                ).first()
                loan_payload = (
                    loan_snapshot.payload
                    if loan_snapshot and isinstance(loan_snapshot.payload, dict)
                    else {}
                )
                requested_amount = loan_payload.get(
                    "requested_amount",
                    loan_payload.get("required_bt_amount"),
                )
            if requested_amount is not None:
                attrs["net_disbursement_amount"] = max(
                    Decimal("0"), Decimal(str(requested_amount)) - calculated_total
                )
        return attrs


class PanStageSerializer(serializers.Serializer):
    contact_number = serializers.CharField(max_length=20)
    pan_number = serializers.CharField(max_length=20)
    pan_image = serializers.FileField(required=False, allow_null=True)
    name_on_pan = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dob_as_per_pan = serializers.DateField(required=False, allow_null=True)

class CustomerDefaulterCheckSerializer(serializers.Serializer):
    pan_number = serializers.CharField(max_length=20, trim_whitespace=True)
    contact_number = serializers.CharField(max_length=20, trim_whitespace=True)

    def to_internal_value(self, data):
        if isinstance(data, dict) and not data.get("pan_number"):
            data = data.copy()
            data["pan_number"] = data.get("pan") or data.get("pan_card_number")
        return super().to_internal_value(data)

    def validate_pan_number(self, value):
        value = (value or "").strip().upper()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_contact_number(self, value):
        value = (value or "").strip()
        digits = re.sub(r"\D", "", value)
        if len(digits) < 10:
            raise serializers.ValidationError("Enter a valid contact number.")
        return value


class LoanRangeSelectionSerializer(serializers.Serializer):
    loan_amount = serializers.DecimalField(max_digits=20, decimal_places=2, required=True)
    avobe_range = serializers.BooleanField(required=False, allow_null=True)


class LendingPartnerBankSerializer(serializers.Serializer):
    lending_partner = serializers.CharField(required=True)
    pincode = serializers.CharField(max_length=10, required=True)
    lending_partner_branch_code = serializers.CharField(max_length=64, required=False, allow_null=True, allow_blank=True)
    lending_partner_branch_name = serializers.CharField(max_length=255, required=True)

    def validate_lending_partner(self, value):
        application = self.context.get("application")
        available_for = None
        if application and application.lead:
            available_for = application.lead.product_subcategory
        return canonicalize_lending_partner_value(value, available_for)



class ProductSelectionBaseSerializer(serializers.Serializer):
    product_type = serializers.ChoiceField(
        choices=[
            ("GENERAL_PURPOSE", "General Purpose"),
            ("AGRI_ALLIED", "Agri Allied"),
            ("MSME", "MSME"),
            ("CONSUMPTION_LOAN", "Consumption Loan"),
            ("INCOME_LOAN", "Income Loan"),
        ],
        required=True,
    )
    product_code = serializers.CharField(required=False, allow_blank=True)
    required_amount = serializers.DecimalField(
        max_digits=14, decimal_places=2, required=False
    )
    tenure_months = serializers.IntegerField(required=False)
    repayment_frequency = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        application = self.context.get("application")
        loan_type = getattr(application, "loan_type", None)
        product_code = attrs.get("product_code")
        if (
            self.context.get("is_complete", False)
            and loan_type == LeadType.SELF_LENDING
            and not product_code
        ):
            raise serializers.ValidationError(
                {"product_code": "Product selection is required for Self Lending."}
            )
        if not product_code:
            return attrs

        product = ProductV2.objects.filter(
            product_code=product_code,
            is_active=True,
        ).first()
        if not product:
            raise serializers.ValidationError(
                {"product_code": "Selected active product was not found."}
            )

        if product.available_for and loan_type not in product.available_for:
            raise serializers.ValidationError(
                {"product_code": "Product is not available for this lead type."}
            )

        amount = attrs.get("required_amount")
        if amount is not None and not (
            product.minimum_ticket_size <= amount <= product.maximum_ticket_size
        ):
            raise serializers.ValidationError(
                {
                    "required_amount": (
                        "Required amount is outside the selected product ticket range."
                    )
                }
            )
        if (
            attrs.get("tenure_months") is not None
            and attrs["tenure_months"] != product.tenure_months
        ):
            raise serializers.ValidationError(
                {"tenure_months": "Tenure does not match selected product."}
            )
        if (
            attrs.get("repayment_frequency")
            and attrs["repayment_frequency"].upper()
            != product.repayment_frequency.upper()
        ):
            raise serializers.ValidationError(
                {
                    "repayment_frequency": (
                        "Repayment frequency does not match selected product."
                    )
                }
            )

        attrs.setdefault("product_type", product.category)
        attrs.setdefault("tenure_months", product.tenure_months)
        attrs.setdefault("repayment_frequency", product.repayment_frequency)
        attrs["interest_rate"] = product.interest_rate
        attrs["ltv"] = product.ltv
        return attrs


class CustomerDefaulterCheckSerializer(serializers.Serializer):
    pan_number = serializers.CharField(max_length=20, trim_whitespace=True)
    contact_number = serializers.CharField(max_length=20, trim_whitespace=True)

    def to_internal_value(self, data):
        if isinstance(data, dict) and not data.get("pan_number"):
            data = data.copy()
            data["pan_number"] = data.get("pan") or data.get("pan_card_number")
        return super().to_internal_value(data)

    def validate_pan_number(self, value):
        value = (value or "").strip().upper()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value

    def validate_contact_number(self, value):
        value = (value or "").strip()
        digits = re.sub(r"\D", "", value)
        if len(digits) < 10:
            raise serializers.ValidationError("Enter a valid contact number.")
        return value


class LoanRangeSelectionSerializer(serializers.Serializer):
    loan_amount = serializers.DecimalField(max_digits=20, decimal_places=2, required=True)
    above_range = serializers.BooleanField(required=False, allow_null=True)

    def to_internal_value(self, data):
        if isinstance(data, dict) and "above_range" not in data and "avobe_range" in data:
            data = data.copy()
            data["above_range"] = data.get("avobe_range")
        return super().to_internal_value(data)


class LendingPartnerBankSerializer(serializers.Serializer):
    lending_partner = serializers.CharField(required=True)
    pincode = serializers.CharField(max_length=10, required=True)
    lending_partner_branch_code = serializers.CharField(max_length=64, required=False, allow_null=True, allow_blank=True)
    lending_partner_branch_name = serializers.CharField(max_length=255, required=True)

    def validate_lending_partner(self, value):
        application = self.context.get("application")
        available_for = None
        if application and application.lead:
            available_for = application.lead.product_subcategory
        return canonicalize_lending_partner_value(value, available_for)



class ProductSelectionSerializer(ProductSelectionBaseSerializer):
    pass


class BasicStageSerializer(serializers.Serializer):
    PROFESSION_ALIAS_MAP = {
        "AGRICULTURE": Profession.AGRICULTURE,
        "ANCILLARY SERVICES": Profession.ANCILLARY_SERVICES,
        "ANCILLARY SERVICES(SELF EMPLOYED)": Profession.ANCILLARY_SERVICES,
        "ANCILLARY SERVICES (SELF EMPLOYED)": Profession.ANCILLARY_SERVICES,
        "ANIMAL HUSBANDRY": Profession.ANIMAL_HUSBANDRY,
        "BUISNESS": Profession.BUISNESS,
        "BUSINESS": Profession.BUSINESS,
        "FIN INSTN/INTERMEDIARY": Profession.FIN_INSTN_INTERMEDIARY,
        "FIN INSTN / INTERMEDIARY": Profession.FIN_INSTN_INTERMEDIARY,
        "HANDICRAFT": Profession.HANDICRAFT,
        "HOUSEWIFE": Profession.HOUSEWIFE,
        "HOME MAKER": Profession.HOME_MAKER,
        "INDIVIDUALS": Profession.INDIVIDUALS,
        "LABOUR": Profession.LABOUR,
        "MANUFACTURING": Profession.MANUFACTURING,
        "MFG": Profession.MFG,
        "NPO": Profession.NPO,
        "OTHER": Profession.OTHER,
        "OTHERS": Profession.OTHERS,
        "POLITICIAN": Profession.POLITICIAN,
        "PROF": Profession.PROF,
        "PROFESSIONAL": Profession.PROFESSIONAL,
        "REAL ESTATE": Profession.REAL_ESTATE,
        "RURAL ARTISANS": Profession.RURAL_ARTISANS,
        "RETIRED": Profession.RETIRED,
        "SALARIED": Profession.SALARIED,
        "SELF EMPLOYED": Profession.SELF_EMPLOYED,
        "SERVICES": Profession.SERVICES,
        "STUDENT": Profession.STUDENT,
        "SERVICE": Profession.SERVICE,
        "TRADE": Profession.TRADE,
        "TRADING": Profession.TRADING,
        "UNEMPLOYED": Profession.UNEMPLOYED,
    }
    CATEGORY_ALIAS_MAP = {
        "GENERAL": Category.GENERAL,
        "OBC": Category.OBC,
        "SCHEDULE CASTE": Category.SC,
        "SC": Category.SC,
        "SCHEDULE TRIBE": Category.ST,
        "ST": Category.ST,
        "OTHER": Category.OTHER,
    }
    QUALIFICATION_ALIAS_MAP = {
        "METRIC": Qualification.METRIC,
        "MATRIC": Qualification.MATRIC,
        "INTERMEDIATE": Qualification.INTERMEDIATE,
        "GRADUATE": Qualification.GRADUATE,
        "ILLITERATE": Qualification.ILLITERATE,
        "PRIMARY": Qualification.PRIMARY,
        "POST GRADUATE": Qualification.POST_GRADUATE,
    }
    RELIGION_ALIAS_MAP = {
        "BUDDHIST": Religion.BUDDHIST,
        "CHRISTIAN": Religion.CHRISTIAN,
        "HINDU": Religion.HINDU,
        "JAIN": Religion.JAIN,
        "MUSLIM": Religion.MUSLIM,
        "OTHERS": Religion.OTHERS,
        "PARSI": Religion.PARSI,
        "SIKH": Religion.SIKH,
        "ZOROASTRIAN": Religion.ZOROASTRIAN,
    }
    LIVING_WITH_ALIAS_MAP = {
        "FAMILY": LivingWith.FAMILY,
        "ALONE": LivingWith.ALONE,
        "FRIENDS": LivingWith.FRIENDS,
        "OTHERS": LivingWith.OTHERS,
    }
    MARITAL_STATUS_ALIAS_MAP = {
        "MARRIED": MaritalStatus.MARRIED,
        "UNMARRIED": MaritalStatus.UNMARRIED,
        "WIDOWED": MaritalStatus.WIDOWED,
        "DIVORCED": MaritalStatus.DIVORCED,
    }

    customer_id = serializers.CharField(max_length=255, required=False, allow_null=True)
    application_id = serializers.CharField(max_length=255, required=False, allow_null=True)
    full_name_as_pan = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    dob = serializers.DateField(required=False, allow_null=True)
    dob_as_per_pan = serializers.DateField(required=False, allow_null=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    alternate_number = serializers.CharField(
        max_length=20, required=False, allow_blank=True, allow_null=True
    )
    # Alias for typo in payload
    alternate_pnone_number = serializers.CharField(
        max_length=20, required=False, allow_blank=True, allow_null=True
    )
    gender = serializers.ChoiceField(choices=Gender.choices, required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    aadhar_number = serializers.CharField(max_length=20, required=False, allow_null=True)
    profession = serializers.ChoiceField(choices=Profession.choices, required=False, allow_null=True, allow_blank=True)
    document_type = serializers.ChoiceField(choices=DocumentType.choices, required=False, allow_null=True)
    document_number = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    loan_type = LeadTypeChoiceField(choices=LeadType.choices, required=False)
    # Additional fields for BT basic stage
    father_full_name = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    marital_status = serializers.ChoiceField(choices=MaritalStatus.choices, required=False, allow_blank=True, allow_null=True)
    annual_income_range = serializers.CharField(max_length=10, required=False, allow_blank=True, allow_null=True)
    total_experience = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    religion = serializers.ChoiceField(choices=Religion.choices, required=False, allow_blank=True, allow_null=True)
    category = serializers.ChoiceField(choices=Category.choices, required=False, allow_blank=True, allow_null=True)
    currently_living_with = serializers.ChoiceField(choices=LivingWith.choices, required=False, allow_blank=True, allow_null=True)
    qualification = serializers.ChoiceField(choices=Qualification.choices, required=False, allow_blank=True, allow_null=True)
    whatsapp_toggle_mobile = serializers.BooleanField(default=False)
    whatsapp_toggle_alternate = serializers.BooleanField(default=False)

    @staticmethod
    def _normalize_choice(value, aliases):
        if not isinstance(value, str):
            return value
        normalized = value.strip().upper().replace("–", "-")
        normalized = " ".join(normalized.split())
        return aliases.get(normalized, value)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            normalized = dict(data)
            if "profession" in normalized:
                normalized["profession"] = self._normalize_choice(
                    normalized.get("profession"), self.PROFESSION_ALIAS_MAP
                )
            if "category" in normalized:
                normalized["category"] = self._normalize_choice(
                    normalized.get("category"), self.CATEGORY_ALIAS_MAP
                )
            if "qualification" in normalized:
                normalized["qualification"] = self._normalize_choice(
                    normalized.get("qualification"), self.QUALIFICATION_ALIAS_MAP
                )
            if "religion" in normalized:
                normalized["religion"] = self._normalize_choice(
                    normalized.get("religion"), self.RELIGION_ALIAS_MAP
                )
            if "currently_living_with" in normalized:
                normalized["currently_living_with"] = self._normalize_choice(
                    normalized.get("currently_living_with"), self.LIVING_WITH_ALIAS_MAP
                )
            if "marital_status" in normalized:
                normalized["marital_status"] = self._normalize_choice(
                    normalized.get("marital_status"), self.MARITAL_STATUS_ALIAS_MAP
                )
            data = normalized
        return super().to_internal_value(data)

    def validate(self, attrs):
        if attrs.get("alternate_number") and attrs["alternate_number"] == attrs["phone_number"]:
            raise serializers.ValidationError("Alternate number cannot match phone number")
        
        application = self.context.get("application")
        is_complete = self.context.get("is_complete", False)
        loan_type = attrs.get("loan_type")
        if not loan_type and application:
            loan_type = getattr(application, "loan_type", None) or getattr(application.lead, "lead_type", None)

        if is_complete and loan_type == LeadType.BALANCE_TRANSFER:
            mandatory_fields = {
                "full_name_as_pan": "Full Name",
                "dob_as_per_pan": "Date of Birth (PAN)",
                "dob": "Date of Birth",
                "father_full_name": "Fathers Full Name",
                "email": "EMail Address",
                "phone_number": "Mobile Number",
                "gender": "Gender",
                "marital_status": "Marital Status",
                "profession": "Profession",
                "annual_income_range": "Annual Income Range",
                "total_experience": "Total Experience",
                "religion": "Religion",
                "category": "Category",
                "currently_living_with": "Currently Living with",
                "qualification": "Qualification",
            }
            for field, label in mandatory_fields.items():
                if not attrs.get(field):
                    raise serializers.ValidationError({field: f"{label} is mandatory"})
        aadhaar_optional_loan_types = {
            LeadType.FRESH,
            LeadType.BALANCE_TRANSFER,
            LeadType.CO_LENDING,
            LeadType.SELF_LENDING,
        }

        if is_complete:
            if loan_type == LeadType.FRESH:
                if attrs.get("document_type") and not attrs.get("document_number"):
                    raise serializers.ValidationError({"document_number": "Document number is required when document type is provided"})
            elif loan_type not in aadhaar_optional_loan_types:
                if not attrs.get("aadhar_number"):
                    raise serializers.ValidationError({"aadhar_number": "Aadhar number is required for non-fresh loans"})
            
        return attrs


class AddressBlockSerializer(serializers.Serializer):
    address_line1 = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    address_line3 = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    pincode = serializers.CharField(max_length=10, required=False, allow_blank=True, allow_null=True)
    state = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    district = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)


class DocumentListSerializer(serializers.ListSerializer):
    def validate(self, data):
        application = self.context.get("application")
        is_complete = self.context.get("is_complete", False)
        stage = self.context.get("stage")
        loan_type = getattr(application, "loan_type", None) if application else None

        # Basic validation for each document in the list to avoid list-style error format
        for i, d in enumerate(data):
            if not d.get("document_type"):
                raise serializers.ValidationError(f"Document type is required for document at index {i+1}")
            if not d.get("status"):
                raise serializers.ValidationError(f"Status is required for document at index {i+1}")

        if (
            is_complete
            and loan_type in {LeadType.BALANCE_TRANSFER, LeadType.SELF_LENDING}
            and stage == ApplicationStage.DOCUMENTS
        ):
            doc_types = {(d.get("document_type"), d.get("subtype")) for d in data}
            
            # 1. LIVE_PHOTO
            # if (DocumentType.LIVE_PHOTO, None) not in doc_types:
            #     raise serializers.ValidationError("Live photo is mandatory for balance transfer")
            
            # 2. AADHAAR FRONT & BACK
            # if (DocumentType.AADHAAR, "AADHAAR_FRONT") not in doc_types:
            #     raise serializers.ValidationError("Aadhaar front is mandatory for balance transfer")
            # if (DocumentType.AADHAAR, "AADHAAR_BACK") not in doc_types:
            #     raise serializers.ValidationError("Aadhaar back is mandatory for balance transfer")
            
            # # 3. Primary Bank (CHEQUE_PRIMARY)
            # if (DocumentType.OTHER, "CHEQUE_PRIMARY") not in doc_types:
            #     raise serializers.ValidationError("Primary bank details (Cheque Primary) are mandatory for balance transfer")

            # Check for mandatory fields in metadata for each mandatory document
            for d in data:
                d_type = d.get("document_type")
                subtype = d.get("subtype")
                metadata = d.get("metadata") or {}
                file_url = d.get("file_url")

                if not file_url:
                    raise serializers.ValidationError(f"File URL is required for {d_type} {subtype or ''}")

                if d_type == DocumentType.AADHAAR and subtype == "AADHAAR_FRONT":
                    if not metadata.get("aadhar_number"):
                        raise serializers.ValidationError("Aadhar number is mandatory in Aadhaar front metadata")
                    if metadata.get("verified") is not True:
                        raise serializers.ValidationError("Aadhaar must be verified")

                if d_type == DocumentType.OTHER and subtype == "CHEQUE_PRIMARY":
                    required_bank_fields = ["bank_name", "account_number", "IFSC_code", "full_name"]
                    for field in required_bank_fields:
                        if not metadata.get(field):
                            raise serializers.ValidationError(f"{field} is mandatory in Primary Bank metadata")
                    if metadata.get("verified") is not True:
                        raise serializers.ValidationError("Primary Bank details must be verified")

        return data


class DocumentUploadSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=DocumentType.choices, required=False, allow_null=True)
    subtype = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(
        choices=DocumentStatus.choices, default=DocumentStatus.UPLOADED, required=False, allow_null=True
    )
    file = serializers.FileField(required=False, allow_null=True)
    file_url = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)

    class Meta:
        list_serializer_class = DocumentListSerializer


class AddressStageSerializer(serializers.Serializer):
    permanent = AddressBlockSerializer(required=False, allow_null=True)
    current_same_as_permanent = serializers.BooleanField(default=False)
    current = AddressBlockSerializer(required=False, allow_null=True)
    mailing = AddressBlockSerializer(required=False)
    residence_type = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    duration_of_stay = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    poa_type = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    poa = DocumentUploadSerializer(required=False, many=True)

    def validate(self, attrs):
        application = self.context.get("application")
        is_complete = self.context.get("is_complete", False)
        loan_type = getattr(application, "loan_type", None) if application else None

        if is_complete:
            if not attrs.get("permanent"):
                raise serializers.ValidationError({"permanent": "Permanent address is mandatory"})
            
            # Validate AddressBlock fields manually since they are now optional in the serializer
            permanent_data = attrs.get("permanent") or {}
            required_block_fields = ["address_line1", "pincode", "state", "district", "city"]
            for field in required_block_fields:
                if not permanent_data.get(field):
                    raise serializers.ValidationError({"permanent": f"Permanent {field.replace('_', ' ')} is mandatory"})

            if loan_type in {LeadType.BALANCE_TRANSFER, LeadType.SELF_LENDING}:
                if not attrs.get("current_same_as_permanent"):
                    if not attrs.get("residence_type"):
                        raise serializers.ValidationError({"residence_type": "Residence type is required"})
                    if not attrs.get("duration_of_stay"):
                        raise serializers.ValidationError({"duration_of_stay": "Duration of stay is required"})
                
                    poa_docs = attrs.get("poa")
                    if not poa_docs:
                        raise serializers.ValidationError({"poa": "Proof of address (POA) is required"})
                    
                    for doc in poa_docs:
                        if not doc.get("file_url"):
                            raise serializers.ValidationError({"poa": "File URL is required for all POA documents"})

            if not attrs.get("current_same_as_permanent"):
                if not attrs.get("current"):
                    raise serializers.ValidationError({"current": "Current address required when not same as permanent"})
                
                current_data = attrs.get("current") or {}
                for field in required_block_fields:
                    if not current_data.get(field):
                        raise serializers.ValidationError({"current": f"Current {field.replace('_', ' ')} is mandatory"})

        return attrs


class SelfieStageSerializer(serializers.Serializer):
    file = serializers.FileField(required=False, allow_null=True)
    file_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    latitude = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    longitude = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    timestamp = serializers.DateTimeField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)
        if is_complete:
            if not attrs.get("file") and not attrs.get("file_url"):
                raise serializers.ValidationError({"file": "Selfie image is required"})
            if not attrs.get("latitude") or not attrs.get("longitude"):
                raise serializers.ValidationError({"location": "Location information is required"})
            if not attrs.get("timestamp"):
                raise serializers.ValidationError({"timestamp": "Timestamp is required"})
        return attrs


class PersonalDetailsSerializer(serializers.Serializer):
    INCOME_SOURCE_ALIAS_MAP = {
        "PROFESSIONAL": IncomeSource.PROFESSIONAL_INCOME,
        "PROFESSIONAL INCOME": IncomeSource.PROFESSIONAL_INCOME,
        "PROFESSIONAL_INCOME": IncomeSource.PROFESSIONAL_INCOME,
        "SALARY": IncomeSource.SALARY,
        "BUSINESS": IncomeSource.BUSINESS,
        "RETIRED": IncomeSource.RETIRED,
        "SELF_EMPLOYED": IncomeSource.SELF_EMPLOYED,
        "SELF EMPLOYED": IncomeSource.SELF_EMPLOYED,
    }

    @staticmethod
    def _normalize_choice(value, aliases):
        if not isinstance(value, str):
            return value
        normalized = value.strip().upper().replace("–", "-")
        normalized = " ".join(normalized.split())
        return aliases.get(normalized, value)

    title = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField()
    dob = serializers.DateField()
    dob_as_per_pan = serializers.DateField()
    place_of_birth = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=Gender.choices)
    mobile_number = serializers.CharField()
    alternate_mobile_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    father_full_name = serializers.CharField(required=False, allow_blank=True)
    mother_full_name = serializers.CharField(required=False, allow_blank=True)
    marital_status = serializers.ChoiceField(choices=MaritalStatus.choices, required=False, allow_blank=True)
    profession = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    occupation = serializers.ChoiceField(choices=Occupation.choices, required=False, allow_blank=True)
    income_source = serializers.ChoiceField(choices=IncomeSource.choices, required=False, allow_blank=True)
    primary_borrower_type = serializers.ChoiceField(
        choices=PrimaryBorrowerType.choices, required=False, allow_blank=True, allow_null=True
    )
    nationality = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nri_status = serializers.ChoiceField(
        choices=NriStatus.choices, required=False, allow_blank=True, allow_null=True
    )
    caste = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    annual_income = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    net_annual_income = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    net_worth = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    foir = serializers.DecimalField(
        max_digits=8,
        decimal_places=3,
        required=True,
        validators=[MinValueValidator(Decimal("0.2")), MaxValueValidator(Decimal("0.9"))],
    )
    religion = serializers.ChoiceField(choices=Religion.choices, required=False)
    category = serializers.ChoiceField(choices=Category.choices, required=False)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            normalized = dict(data)
            if "income_source" in normalized:
                normalized["income_source"] = self._normalize_choice(
                    normalized.get("income_source"), self.INCOME_SOURCE_ALIAS_MAP
                )
            data = normalized
        return super().to_internal_value(data)


class AddressSecondarySerializer(AddressStageSerializer):
    poa = DocumentUploadSerializer(required=False, many=True)


class GoldItemSerializer(serializers.Serializer):
    type_of_jewellery = serializers.ChoiceField(choices=JewelleryType.choices)
    number_of_articles = serializers.IntegerField()
    item_index = serializers.IntegerField(required=False, default=None)
    purity = serializers.CharField(required=False, allow_blank=True)
    gross_weight = serializers.DecimalField(max_digits=14, decimal_places=3)
    stone_weight = serializers.DecimalField(max_digits=14, decimal_places=3, required=False)
    net_weight = serializers.DecimalField(max_digits=14, decimal_places=3)
    impurity_deducted = serializers.DecimalField(max_digits=14, decimal_places=3, required=False)
    net_adjusted_weight = serializers.DecimalField(max_digits=14, decimal_places=3)
    percent_of_gold = serializers.DecimalField(max_digits=8, decimal_places=3, required=False)
    actual_gold_rate = serializers.DecimalField(max_digits=16, decimal_places=3, required=False)
    gross_value = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    net_value = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    net_adjusted_value = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    front_image_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    back_image_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    weighing_machine_image_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    appraiser_certificate_image_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.JSONField(required=False)

    def validate(self, attrs):
        # Enforce URL-only uploads; reject raw files
        forbidden = ["front_image", "back_image", "weighing_machine_image", "appraiser_certificate_image"]
        initial = getattr(self, "initial_data", {}) or {}
        for key in forbidden:
            if key in initial:
                raise serializers.ValidationError("File uploads are not allowed; use presigned URLs.")
        return attrs


class GoldPacketSerializer(serializers.Serializer):
    packet_id = serializers.CharField()
    barcode_id = serializers.CharField(required=False, allow_blank=True)
    gross_weight = serializers.DecimalField(max_digits=14, decimal_places=3, required=False)
    gross_value = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    net_adjusted_weight = serializers.DecimalField(max_digits=14, decimal_places=3, required=False)
    net_adjusted_value = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    appraiser_id = serializers.CharField(required=False, allow_blank=True)
    appraiser_name = serializers.CharField(required=False, allow_blank=True)
    appraiserId = serializers.CharField(required=False, allow_blank=True, write_only=True)
    appraiserName = serializers.CharField(required=False, allow_blank=True, write_only=True)
    items = GoldItemSerializer(many=True)

    def validate(self, attrs):
        if attrs.get("appraiser_id") in (None, "") and attrs.get("appraiserId"):
            attrs["appraiser_id"] = attrs.get("appraiserId")
        if attrs.get("appraiser_name") in (None, "") and attrs.get("appraiserName"):
            attrs["appraiser_name"] = attrs.get("appraiserName")
        items = attrs.get("items") or []
        errors = {}

        def _to_decimal(value):
            if value in (None, ""):
                return None
            try:
                return Decimal(str(value))
            except Exception:
                return None

        def _sum_item(field):
            total = Decimal("0")
            for item in items:
                if not isinstance(item, dict):
                    continue
                val = _to_decimal(item.get(field))
                if val is not None:
                    total += val
            return total

        gross_weight_total = _sum_item("gross_weight")
        gross_value_total = _sum_item("gross_value")
        net_adjusted_weight_total = _sum_item("net_adjusted_weight")
        net_adjusted_value_total = _sum_item("net_adjusted_value")

        packet_gross_weight = _to_decimal(attrs.get("gross_weight"))
        packet_gross_value = _to_decimal(attrs.get("gross_value"))
        packet_net_adjusted_weight = _to_decimal(attrs.get("net_adjusted_weight"))
        packet_net_adjusted_value = _to_decimal(attrs.get("net_adjusted_value"))

        if packet_gross_weight is not None and packet_gross_weight != gross_weight_total:
            errors["gross_weight"] = (
                "Gross weight must equal sum of item gross weights."
            )
        if packet_gross_value is not None and packet_gross_value != gross_value_total:
            errors["gross_value"] = (
                "Gross value must equal sum of item gross values."
            )
        if (
            packet_net_adjusted_weight is not None
            and packet_net_adjusted_weight != net_adjusted_weight_total
        ):
            errors["net_adjusted_weight"] = (
                "Net adjusted weight must equal sum of item net adjusted weights."
            )
        if (
            packet_net_adjusted_value is not None
            and packet_net_adjusted_value != net_adjusted_value_total
        ):
            errors["net_adjusted_value"] = (
                "Net adjusted value must equal sum of item net adjusted values."
            )

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Drop None item_index so merge logic doesn't treat it as a valid index
        cleaned = []
        for item in data.get("items") or []:
            if isinstance(item, dict) and item.get("item_index") is None:
                item = dict(item)
                item.pop("item_index", None)
            cleaned.append(item)
        data["items"] = cleaned
        return data


class LoanDetailsSerializer(serializers.Serializer):
    # Canonical fields
    existing_loan_amount = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    eligible_amount = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    requested_amount = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    number_of_articles = serializers.IntegerField(required=False)
    gross_weight = serializers.DecimalField(max_digits=14, decimal_places=3, required=False)
    net_weight = serializers.DecimalField(max_digits=14, decimal_places=3, required=False)
    interest_rate = serializers.DecimalField(max_digits=8, decimal_places=3, required=False)
    tenure_years = serializers.IntegerField(required=False)
    tenure_months = serializers.IntegerField(required=False)
    type_of_emi = serializers.ChoiceField(choices=EmiType.choices, required=False)
    interest_type = serializers.ChoiceField(choices=InterestType.choices, required=False)
    repayment_frequency = serializers.ChoiceField(choices=RepaymentFrequency.choices, required=False)
    category = serializers.ChoiceField(choices=CategoryType.choices, required=False)
    disbursement_type = serializers.ChoiceField(choices=DisbursementType.choices, required=False)
    bank_name = serializers.CharField(max_length=255, required=False)
    state = serializers.CharField(max_length=255, required=False)
    district = serializers.CharField(max_length=255, required=False)
    bank_branch = serializers.CharField(required=False, allow_blank=True)
    bank_branch_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    purpose = serializers.CharField(required=False, allow_blank=True)
    bt_category = serializers.ChoiceField(choices=["INTERNAL", "EXTERNAL"], required=False)
    credit_score = serializers.IntegerField(required=False)
    credit_score_status = serializers.CharField(required=False, allow_blank=True)
    bank_appraiser = serializers.CharField(required=False, allow_blank=True)
    bank_appraiser_id = serializers.CharField(required=False, allow_blank=True)
    bank_appraiser_name = serializers.CharField(required=False, allow_blank=True)
    loan_type = LeadTypeChoiceField(choices=LeadType.choices, required=False)
    loan_subcategory = serializers.ChoiceField(
        choices=LoanSubCategory.choices,
        required=False,
        allow_blank=True,
    )
    partner_branch_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    partner_branch_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    partner_product_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    agreement_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    spread_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ltr = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    ltr_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    interest_start_date = serializers.DateField(required=False, allow_null=True)
    loan_maturity_date = serializers.DateField(required=False, allow_null=True)
    first_repayment_date = serializers.DateField(required=False, allow_null=True)
    processing_fee = serializers.DecimalField(max_digits=14, decimal_places=2, required=False, read_only=True)
    stamp_duty = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    insurance_charges = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    documentation_charges = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    other_charges = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    total_charges = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    compliance = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    source_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    consent_timestamp = serializers.DateTimeField(required=False, allow_null=True)
    consent_ip = serializers.IPAddressField(required=False, allow_null=True)
    reference_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    multi_appraisal = serializers.BooleanField(required=False)
    number_of_animal_cattle = serializers.IntegerField(required=False)
    cattleImageUrl = serializers.URLField(required=False, allow_blank=True, allow_null=True)

    # Figma / mobile aliases mapped to canonical API keys
    BT_LOAN_ALIAS_MAP = {
        "total_existing_loan_amount": "existing_loan_amount",
        "total_article": "number_of_articles",
        "total_articles": "number_of_articles",
        "total_gross_weight": "gross_weight",
        "total_net_weight": "net_weight",
        "purpose_of_loan": "purpose",
        "eligible_bt_amount": "eligible_amount",
        "required_bt_amount": "requested_amount",
    }

    NUMERIC_STRING_KEYS = {
        "existing_loan_amount",
        "eligible_amount",
        "requested_amount",
        "number_of_articles",
        "gross_weight",
        "net_weight",
        "total_existing_loan_amount",
        "total_article",
        "total_articles",
        "total_gross_weight",
        "total_net_weight",
        "eligible_bt_amount",
        "required_bt_amount",
        "interest_rate",
        "processing_fee",
        "stamp_duty",
        "insurance_charges",
        "documentation_charges",
        "other_charges",
        "total_charges",
        "ltr_percentage",
        "tenure_months",
        "tenure_years",
    }

    @staticmethod
    def _clean_numeric_string(value):
        if not isinstance(value, str):
            return value
        cleaned = value.replace(",", "").replace("₹", "").replace("Rs.", "").replace("Rs", "").strip()
        return cleaned

    def to_internal_value(self, data):
        if isinstance(data, dict):
            normalized = dict(data)
        elif hasattr(data, "copy"):
            normalized = data.copy()
        else:
            normalized = data

        if isinstance(normalized, dict):
            for alias_key, canonical_key in self.BT_LOAN_ALIAS_MAP.items():
                if alias_key in normalized and canonical_key not in normalized:
                    normalized[canonical_key] = normalized.get(alias_key)
            if normalized.get("number_of_animal_cattle") == "":
                normalized.pop("number_of_animal_cattle")
            repayment_frequency = normalized.get("repayment_frequency")
            if isinstance(repayment_frequency, str):
                normalized["repayment_frequency"] = repayment_frequency.strip().upper()
            for key in self.NUMERIC_STRING_KEYS:
                if key in normalized:
                    normalized[key] = self._clean_numeric_string(normalized.get(key))
            # Clean empty strings for date fields to prevent validation failures
            date_fields = ["loan_maturity_date", "interest_start_date", "first_repayment_date"]
            for field in date_fields:
                if field in normalized and normalized[field] == "":
                    normalized[field] = None

        return super().to_internal_value(normalized)

    def validate(self, attrs):
        application = self.context.get("application")
        is_complete = self.context.get("is_complete", False)
        loan_type = attrs.get("loan_type")
        if not loan_type and application:
            loan_type = getattr(application, "loan_type", None) or getattr(application.lead, "lead_type", None)

        if is_complete and loan_type == LeadType.BALANCE_TRANSFER:
            mandatory_fields = {
                "existing_loan_amount": "Total Existing Loan Amount",
                "number_of_articles": "Total Articles",
                "gross_weight": "Total Gross Weight",
                "net_weight": "Total Net Weight",
                "purpose": "Purpose of Loan",
                "bt_category": "BT Category",
                "eligible_amount": "Eligible BT amount",
                "requested_amount": "Required BT amount",
                "credit_score_status": "Credit Score Status",
            }
            for field, label in mandatory_fields.items():
                if not attrs.get(field):
                    raise serializers.ValidationError({field: f"{label} is mandatory"})
        elif is_complete and loan_type == LeadType.SELF_LENDING:
            mandatory_fields = {
                "eligible_amount": "Eligible Amount",
                "requested_amount": "Required Amount",
                "interest_rate": "Interest Rate",
                "tenure_years": "Tenure",
                "type_of_emi": "Type of EMI",
                "interest_type": "Interest Type",
                "repayment_frequency": "Repayment Frequency",
                "category": "Category",
                "disbursement_type": "Disbursement Type",
                "purpose": "Purpose of Loan",
            }
            missing = {
                field: f"{label} is mandatory"
                for field, label in mandatory_fields.items()
                if attrs.get(field) in (None, "")
            }
            if missing:
                raise serializers.ValidationError(missing)

        errors = {}
        loan_subcategory = attrs.get("loan_subcategory")
        if loan_subcategory and loan_subcategory != LoanSubCategory.FRESH:
            errors["loan_subcategory"] = "Only Fresh loan sub category is supported right now."
        amount = attrs.get("requested_amount")
        # For Fresh loans, appraiser details are not required regardless of amount as per UI design.
        if (
            amount is not None
            and amount > 500000
            and loan_type != LeadType.BALANCE_TRANSFER
            and loan_subcategory != LoanSubCategory.FRESH
        ):
            if not attrs.get("bank_appraiser_id"):
                errors["bank_appraiser_id"] = "Bank appraiser id is required for loans above 500000."
            if not attrs.get("bank_appraiser_name"):
                errors["bank_appraiser_name"] = "Bank appraiser name is required for loans above 500000."
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class PledgeCardSerializer(serializers.Serializer):
    """Pledge Card stage for Balance Transfer flow."""
    pledge_cards = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )

    def validate(self, attrs):
        application = self.context.get("application")
        is_complete = self.context.get("is_complete", False)
        pledge_cards = attrs.get("pledge_cards", [])

        if is_complete:
            if not pledge_cards:
                raise serializers.ValidationError({"pledge_cards": "At least one pledge card is required."})
            
            if len(pledge_cards) > 10:
                raise serializers.ValidationError({"pledge_cards": "Maximum 10 pledge cards are allowed."})

            # Check for SELF relationship in at least one card
            has_self_relationship = any(
                str(card.get("relationship", "")).upper() == "SELF" 
                for card in pledge_cards if isinstance(card, dict)
            )
            if not has_self_relationship:
                raise serializers.ValidationError({"pledge_cards": "At least one pledge card with 'SELF' relationship is mandatory."})

            required_fields = ["relationship", "lender", "loan_amount", "number_of_articles", "gross_weight", "net_weight", "roi"]
            for i, card in enumerate(pledge_cards):
                if not isinstance(card, dict):
                    raise serializers.ValidationError({"pledge_cards": f"Item {i+1} must be a dictionary."})
                
                # Mandatory field checks
                for field in required_fields:
                    if not card.get(field):
                        label = field.replace("_", " ").title()
                        raise serializers.ValidationError({"pledge_cards": f"Item {i+1}: {label} is required."})
                
                # Image validation
                images = card.get("images", [])
                if not isinstance(images, list) or not images:
                    raise serializers.ValidationError({"pledge_cards": f"Item {i+1}: At least one image is mandatory."})
                if len(images) > 6:
                    raise serializers.ValidationError({"pledge_cards": f"Item {i+1}: Maximum 6 images are allowed per pledge card."})
                
                for j, img in enumerate(images):
                    if isinstance(img, dict):
                        if not img.get("file_url"):
                            raise serializers.ValidationError({"pledge_cards": f"Item {i+1}, Image {j+1}: File URL is required."})
                    elif not isinstance(img, str):
                        raise serializers.ValidationError({"pledge_cards": f"Item {i+1}, Image {j+1}: Must be a string URL or a dictionary."})

        return attrs


class BankDetailsSerializer(serializers.Serializer):
    # Standard fields
    cheque_image_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.JSONField(required=False)
    bank_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    account_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    customer_name_as_per_bank = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ifsc_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    branch_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # BT specific fields
    bt_bank_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    co_lending_product = serializers.BooleanField(required=False, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    district = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    branch_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        application = self.context.get("application")
        is_complete = self.context.get("is_complete", False)
        loan_type = getattr(application, "loan_type", None) if application else None

        initial = getattr(self, "initial_data", {}) or {}
        if "cheque_image" in initial:
            raise serializers.ValidationError("File uploads are not allowed; use presigned URLs for cheque_image.")

        if is_complete:
            if loan_type == LeadType.BALANCE_TRANSFER:
                mandatory_fields = {
                    "bt_bank_name": "Lending Bank",
                    "co_lending_product": "Co-Lending Product Toggle",
                    "state": "State",
                    "district": "District",
                    "branch_name": "Branch",
                }
                for field, label in mandatory_fields.items():
                    if attrs.get(field) is None or (isinstance(attrs.get(field), str) and not attrs.get(field).strip()):
                        raise serializers.ValidationError({field: f"{label} is mandatory"})
            else:
                mandatory_fields = {
                    "bank_name": "Bank Name",
                    "account_number": "Account Number",
                    "customer_name_as_per_bank": "Customer Name as per Bank",
                    "ifsc_code": "IFSC Code",
                }
                for field, label in mandatory_fields.items():
                    if not attrs.get(field):
                        raise serializers.ValidationError({field: f"{label} is mandatory"})

        return attrs


class BTCustomerVisitSerializer(serializers.Serializer):
    """Customer Visit stage for Balance Transfer flow."""
    # Mandatory images (presigned URLs or objects)
    customer_visit_image_url = serializers.JSONField(required=False, allow_null=True)
    house_exterior_image_url = serializers.JSONField(required=False, allow_null=True)
    # Optional images
    house_interior_image_url = serializers.JSONField(required=False, allow_null=True)
    door_number_image_url = serializers.JSONField(required=False, allow_null=True)
    street_view_1_image_url = serializers.JSONField(required=False, allow_null=True)
    street_view_2_image_url = serializers.JSONField(required=False, allow_null=True)
    # GPS coordinates embedded in the customer visit image (mandatory)
    latitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=10, decimal_places=7, required=False, allow_null=True)
    timestamp = serializers.DateTimeField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.JSONField(required=False)

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)

        def _get_url(val):
            if isinstance(val, str):
                return val
            if isinstance(val, dict):
                return val.get("file_url")
            return None

        def _get_latitude():
            lat = attrs.get("latitude")
            if lat:
                return lat
            cvi = attrs.get("customer_visit_image_url")
            if isinstance(cvi, dict):
                return cvi.get("latitude")
            return None

        def _get_longitude():
            lon = attrs.get("longitude")
            if lon:
                return lon
            cvi = attrs.get("customer_visit_image_url")
            if isinstance(cvi, dict):
                return cvi.get("longitude")
            return None

        if is_complete:
            mandatory_url_fields = {
                "customer_visit_image_url": "Customer Visit Image",
                "house_exterior_image_url": "House Exterior Image",
            }
            for field, label in mandatory_url_fields.items():
                val = attrs.get(field)
                if not _get_url(val):
                    raise serializers.ValidationError({field: f"{label} is mandatory"})

            if not _get_latitude():
                raise serializers.ValidationError({"latitude": "Latitude is mandatory"})
            if not _get_longitude():
                raise serializers.ValidationError({"longitude": "Longitude is mandatory"})
        return attrs


class CustomerVisitSerializer(serializers.Serializer):
    metadata = serializers.JSONField(required=False)


class WaiverSerializer(serializers.Serializer):
    metadata = serializers.JSONField(required=False)


# Processing fee waiver: max waiver % allowed per bureau score slab
_WAIVER_MAX_PCT = {
    "above_700": Decimal("75"),
    "600_700": Decimal("50"),
    "500_600": Decimal("25"),
    "below_500": Decimal("0"),
}


def _waiver_limit_for_score(bureau_score):
    if bureau_score is None:
        return Decimal("0")
    if bureau_score > 700:
        return _WAIVER_MAX_PCT["above_700"]
    if bureau_score >= 600:
        return _WAIVER_MAX_PCT["600_700"]
    if bureau_score >= 500:
        return _WAIVER_MAX_PCT["500_600"]
    return _WAIVER_MAX_PCT["below_500"]


# Processing fee rate per bureau score slab (% of loan amount)
_PF_RATE = {
    "above_700": Decimal("0.15"),
    "600_700": Decimal("0.20"),
    "500_600": Decimal("0.35"),
    "450_500": Decimal("0.75"),
    "below_450": Decimal("1.00"),
}


def _pf_rate_for_score(bureau_score):
    if bureau_score is None:
        return _PF_RATE["below_450"]
    if bureau_score > 700:
        return _PF_RATE["above_700"]
    if bureau_score >= 600:
        return _PF_RATE["600_700"]
    if bureau_score >= 500:
        return _PF_RATE["500_600"]
    if bureau_score >= 450:
        return _PF_RATE["450_500"]
    return _PF_RATE["below_450"]


class BTWaiverSerializer(serializers.Serializer):
    """Waiver stage for Balance Transfer flow."""
    waiver_opted = serializers.BooleanField(default=False)
    # Required only when waiver_opted=True
    waiver_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    proof_1_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    proof_2_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.JSONField(required=False)

    def validate(self, attrs):
        if not attrs.get("waiver_opted"):
            return attrs
        waiver_pct = attrs.get("waiver_percentage")
        if waiver_pct is None:
            raise serializers.ValidationError(
                {"waiver_percentage": "Required when waiver is opted."}
            )
        application = self.context.get("application")
        bureau_score = getattr(application, "bureau_score", None) if application else None
        # If bureau score is not yet available, skip slab validation
        if bureau_score is not None:
            max_pct = _waiver_limit_for_score(bureau_score)
            if max_pct == Decimal("0"):
                raise serializers.ValidationError(
                    {"waiver_percentage": "Waiver is not allowed for the current bureau score."}
                )
            if Decimal(str(waiver_pct)) > max_pct:
                raise serializers.ValidationError(
                    {"waiver_percentage": f"Waiver cannot exceed {max_pct}% for bureau score {bureau_score}."}
                )
        if not attrs.get("proof_1_url"):
            raise serializers.ValidationError(
                {"proof_1_url": "Proof image is required when waiver is opted."}
            )
        return attrs


class ReferenceSerializer(serializers.Serializer):
    relationship = serializers.ChoiceField(choices=Relation.choices)
    full_name = serializers.CharField(max_length=100)
    mobile_number = serializers.CharField(max_length=10)

    def validate_mobile_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
        return value


class BTAdditionalDetailsSerializer(serializers.Serializer):
    """Additional Details stage for Balance Transfer flow."""
    RENTAL_INCOME_ALIAS_MAP = {
        ">75K": RentalIncome.ABOVE_75K,
        "75K+": RentalIncome.ABOVE_75K,
        "ABOVE_75K": RentalIncome.ABOVE_75K,
        "50-70K": RentalIncome.BETWEEN_50K_75K,
        "50-75K": RentalIncome.BETWEEN_50K_75K,
        "BETWEEN_50K_75K": RentalIncome.BETWEEN_50K_75K,
        "25-50K": RentalIncome.BETWEEN_25K_50K,
        "BETWEEN_25K_50K": RentalIncome.BETWEEN_25K_50K,
        "<25K": RentalIncome.BELOW_25K,
        "BELOW_25K": RentalIncome.BELOW_25K,
    }
    ANNUAL_INCOME_FAMILY_ALIAS_MAP = {
        ">20L": AnnualIncomeFamilyRange.ABOVE_20L,
        "20L+": AnnualIncomeFamilyRange.ABOVE_20L,
        "ABOVE_20L": AnnualIncomeFamilyRange.ABOVE_20L,
        "15-20L": AnnualIncomeFamilyRange.BETWEEN_15L_20L,
        "BETWEEN_15L_20L": AnnualIncomeFamilyRange.BETWEEN_15L_20L,
        "10-15L": AnnualIncomeFamilyRange.BETWEEN_10L_15L,
        "BETWEEN_10L_15L": AnnualIncomeFamilyRange.BETWEEN_10L_15L,
        "<10L": AnnualIncomeFamilyRange.BELOW_10L,
        "BELOW_10L": AnnualIncomeFamilyRange.BELOW_10L,
    }
    HOUSE_OWNERSHIP_ALIAS_MAP = {
        "NATIVE OWNED": HouseOwnership.NATIVE_OWNED,
        "PARENTAL": HouseOwnership.NATIVE_OWNED,
        "RENTED": HouseOwnership.RENTED,
        "SELF OWNED": HouseOwnership.SELF_OWNED,
        "OWNED": HouseOwnership.SELF_OWNED,
    }

    # Income fields
    rental_income = serializers.ChoiceField(
        choices=RentalIncome.choices, required=False, allow_blank=True, allow_null=True
    )
    annual_income_family_range = serializers.ChoiceField(choices=AnnualIncomeFamilyRange.choices, required=False, allow_null=True)
    house_ownership = serializers.ChoiceField(choices=HouseOwnership.choices, required=False, allow_null=True)
    # Due diligence checklist (varies by house_ownership)
    due_diligence_checklist = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    # References
    reference_1 = ReferenceSerializer(required=False, allow_null=True)
    reference_2 = ReferenceSerializer(required=False, allow_null=True)

    @staticmethod
    def _normalize_choice(value, aliases):
        if not isinstance(value, str):
            return value
        normalized = value.strip().upper().replace("–", "-").replace("₹", "")
        normalized = " ".join(normalized.split())
        return aliases.get(normalized, value)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            normalized = dict(data)
            if "rental_income" in normalized:
                normalized["rental_income"] = self._normalize_choice(
                    normalized.get("rental_income"),
                    self.RENTAL_INCOME_ALIAS_MAP,
                )
            if "annual_income_family_range" in normalized:
                normalized["annual_income_family_range"] = self._normalize_choice(
                    normalized.get("annual_income_family_range"),
                    self.ANNUAL_INCOME_FAMILY_ALIAS_MAP,
                )
            if "house_ownership" in normalized:
                normalized["house_ownership"] = self._normalize_choice(
                    normalized.get("house_ownership"),
                    self.HOUSE_OWNERSHIP_ALIAS_MAP,
                )
            data = normalized
        return super().to_internal_value(data)

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)
        
        if is_complete:
            mandatory_fields = {
                "rental_income": "Rental Income",
                "annual_income_family_range": "Annual Income Range",
                "house_ownership": "House Ownership",
                "reference_1": "Reference 1",
                "reference_2": "Reference 2",
            }
            for field, label in mandatory_fields.items():
                if not attrs.get(field):
                    raise serializers.ValidationError({field: f"{label} is mandatory"})
            
            if not attrs.get("due_diligence_checklist"):
                raise serializers.ValidationError({"due_diligence_checklist": "Due diligence checklist is mandatory"})

        r1_mobile = attrs.get("reference_1", {}).get("mobile_number", "") if attrs.get("reference_1") else ""
        r2_mobile = attrs.get("reference_2", {}).get("mobile_number", "") if attrs.get("reference_2") else ""
        application = self.context.get("application")
        customer_mobile = ""
        if application and application.lead:
            customer_mobile = (application.lead.contact_number or "").lstrip("+91").lstrip("91")[-10:]
        if r1_mobile and r2_mobile and r1_mobile == r2_mobile:
            raise serializers.ValidationError(
                {"reference_2": "Reference #2 mobile must differ from Reference #1."}
            )
        for label, mobile in [("reference_1", r1_mobile), ("reference_2", r2_mobile)]:
            if customer_mobile and mobile and mobile == customer_mobile:
                raise serializers.ValidationError(
                    {label: "Reference mobile must differ from customer mobile."}
                )
        return attrs


class AdditionalDetailsSerializer(serializers.Serializer):
    RENTAL_INCOME_ALIAS_MAP = {
        ">75K": RentalIncome.ABOVE_75K,
        "75K+": RentalIncome.ABOVE_75K,
        "ABOVE_75K": RentalIncome.ABOVE_75K,
        "50-70K": RentalIncome.BETWEEN_50K_75K,
        "50-75K": RentalIncome.BETWEEN_50K_75K,
        "BETWEEN_50K_75K": RentalIncome.BETWEEN_50K_75K,
        "25-50K": RentalIncome.BETWEEN_25K_50K,
        "BETWEEN_25K_50K": RentalIncome.BETWEEN_25K_50K,
        "<25K": RentalIncome.BELOW_25K,
        "BELOW_25K": RentalIncome.BELOW_25K,
    }
    ANNUAL_INCOME_FAMILY_ALIAS_MAP = {
        ">20L": AnnualIncomeFamilyRange.ABOVE_20L,
        "20L+": AnnualIncomeFamilyRange.ABOVE_20L,
        "ABOVE_20L": AnnualIncomeFamilyRange.ABOVE_20L,
        "15-20L": AnnualIncomeFamilyRange.BETWEEN_15L_20L,
        "BETWEEN_15L_20L": AnnualIncomeFamilyRange.BETWEEN_15L_20L,
        "10-15L": AnnualIncomeFamilyRange.BETWEEN_10L_15L,
        "BETWEEN_10L_15L": AnnualIncomeFamilyRange.BETWEEN_10L_15L,
        "<10L": AnnualIncomeFamilyRange.BELOW_10L,
        "BELOW_10L": AnnualIncomeFamilyRange.BELOW_10L,
    }
    HOUSE_OWNERSHIP_ALIAS_MAP = {
        "NATIVE OWNED": HouseOwnership.NATIVE_OWNED,
        "PARENTAL": HouseOwnership.NATIVE_OWNED,
        "RENTED": HouseOwnership.RENTED,
        "SELF OWNED": HouseOwnership.SELF_OWNED,
        "OWNED": HouseOwnership.SELF_OWNED,
    }

    is_employee = serializers.BooleanField(default=False)
    nominee_relation = serializers.ChoiceField(
        choices=Relation.choices, required=False, allow_blank=True, allow_null=True
    )
    nominee_full_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nominee_contact_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Income fields
    rental_income = serializers.ChoiceField(
        choices=RentalIncome.choices, required=False, allow_blank=True, allow_null=True
    )
    annual_income_family_range = serializers.ChoiceField(
        choices=AnnualIncomeFamilyRange.choices, required=False, allow_null=True
    )
    house_ownership = serializers.ChoiceField(
        choices=HouseOwnership.choices, required=False, allow_null=True
    )
    # Due diligence checklist
    due_diligence_checklist = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    # References
    reference_1 = ReferenceSerializer(required=False, allow_null=True)
    reference_2 = ReferenceSerializer(required=False, allow_null=True)

    @staticmethod
    def _normalize_choice(value, aliases):
        if not isinstance(value, str):
            return value
        normalized = value.strip().upper().replace("–", "-").replace("₹", "")
        normalized = " ".join(normalized.split())
        return aliases.get(normalized, value)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            normalized = dict(data)
            if "rental_income" in normalized:
                normalized["rental_income"] = self._normalize_choice(
                    normalized.get("rental_income"),
                    self.RENTAL_INCOME_ALIAS_MAP,
                )
            if "annual_income_family_range" in normalized:
                normalized["annual_income_family_range"] = self._normalize_choice(
                    normalized.get("annual_income_family_range"),
                    self.ANNUAL_INCOME_FAMILY_ALIAS_MAP,
                )
            if "house_ownership" in normalized:
                normalized["house_ownership"] = self._normalize_choice(
                    normalized.get("house_ownership"),
                    self.HOUSE_OWNERSHIP_ALIAS_MAP,
                )
            data = normalized
        return super().to_internal_value(data)

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)
        if is_complete:
            # For now, we don't make these mandatory for non-BT as it might break existing flows
            # unless the user explicitly requested it. The curl has is_complete: true.
            pass

        r1_mobile = attrs.get("reference_1", {}).get("mobile_number", "") if attrs.get("reference_1") else ""
        r2_mobile = attrs.get("reference_2", {}).get("mobile_number", "") if attrs.get("reference_2") else ""
        application = self.context.get("application")
        customer_mobile = ""
        if application and application.lead:
            customer_mobile = (application.lead.contact_number or "").lstrip("+91").lstrip("91")[-10:]

        if r1_mobile and r1_mobile == customer_mobile:
            raise serializers.ValidationError({"reference_1": "Reference 1 mobile cannot match customer mobile"})
        if r2_mobile and r2_mobile == customer_mobile:
            raise serializers.ValidationError({"reference_2": "Reference 2 mobile cannot match customer mobile"})
        if r1_mobile and r2_mobile and r1_mobile == r2_mobile:
            raise serializers.ValidationError({"reference_2": "Reference 2 mobile cannot match Reference 1 mobile"})

        return attrs


class EligibilityStageSerializer(serializers.Serializer):
    """Eligibility stage for Balance Transfer flow."""
    credit_bureau_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    score_band = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    score_color = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    score_value = serializers.IntegerField(required=False, allow_null=True)
    metadata = serializers.JSONField(required=False)

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)
        if is_complete:
            mandatory_fields = {
                "credit_bureau_url": "Credit Bureau URL",
                "score_band": "Score Band",
                "score_value": "Score Value",
            }
            for field, label in mandatory_fields.items():
                if attrs.get(field) is None or (isinstance(attrs.get(field), str) and not attrs.get(field).strip()):
                    raise serializers.ValidationError({field: f"{label} is mandatory"})
        return attrs


class ImportPincodeFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    truncate = serializers.BooleanField(default=False)


class ImportBranchFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    truncate = serializers.BooleanField(default=False)
    lender_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bank_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class PresignDocumentSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=DocumentType.choices)
    subtype = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    filename = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    content_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class PresignGetDocumentSerializer(serializers.Serializer):
    document_type = serializers.ChoiceField(choices=DocumentType.choices, required=False)
    subtype = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    file_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    object_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class LeadAutoClosureSettingSerializer(serializers.ModelSerializer):
    lead_type = LeadTypeChoiceField(choices=LeadType.choices)
    auto_closure_days = serializers.IntegerField(min_value=1, max_value=3650)

    class Meta:
        model = LeadAutoClosureSetting
        fields = "__all__"
        # Disable auto-generated UniqueTogetherValidator — it checks ALL rows
        # including soft-deleted ones. Our custom validate() handles this correctly.
        validators = []

    def validate(self, attrs):
        """Check uniqueness only among active (non-deleted) records."""
        lead_type = attrs.get("lead_type", getattr(self.instance, "lead_type", None))
        product_subcategory = attrs.get("product_subcategory", getattr(self.instance, "product_subcategory", None))

        if lead_type and product_subcategory:
            qs = LeadAutoClosureSetting.objects.filter(
                lead_type=lead_type,
                product_subcategory=product_subcategory,
                is_active=True,
            )
            # Exclude current instance during updates
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "The fields lead_type, product_subcategory must make a unique set."
                )
        return attrs


class AmountTransferredSerializer(serializers.Serializer):
    """Amount Transferred stage for Balance Transfer flow."""
    amount_transferred_status = serializers.ChoiceField(choices=["Yes", "No", "On-Hold"])
    reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.JSONField(required=False)

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)
        status = attrs.get("amount_transferred_status")

        if is_complete:
            if not status:
                raise serializers.ValidationError({"amount_transferred_status": "Status is mandatory"})
            
            if status == "No":
                if not attrs.get("reason"):
                    raise serializers.ValidationError({"reason": "Reason is mandatory when status is No"})
                if not attrs.get("remarks"):
                    raise serializers.ValidationError({"remarks": "Remarks are mandatory when status is No"})
            
            if status == "On-Hold":
                if not attrs.get("reason"):
                    raise serializers.ValidationError({"reason": "Reason is mandatory when status is On-Hold"})

        return attrs


class GoldReceivedSerializer(serializers.Serializer):
    """Gold Received stage for Balance Transfer flow."""
    gold_received_status = serializers.ChoiceField(choices=["Yes", "No", "On-Hold"])
    reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.JSONField(required=False)

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)
        status = attrs.get("gold_received_status")

        if is_complete:
            if not status:
                raise serializers.ValidationError({"gold_received_status": "Status is mandatory"})
            
            if status == "No":
                if not attrs.get("reason"):
                    raise serializers.ValidationError({"reason": "Reason is mandatory when status is No"})
                if not attrs.get("remarks"):
                    raise serializers.ValidationError({"remarks": "Remarks are mandatory when status is No"})
            
            if status == "On-Hold":
                if not attrs.get("reason"):
                    raise serializers.ValidationError({"reason": "Reason is mandatory when status is On-Hold"})

        return attrs


class GoldSubmittedSerializer(serializers.Serializer):
    """Gold Submitted stage for Balance Transfer flow."""
    gold_submitted_status = serializers.ChoiceField(choices=["Yes", "No", "On-Hold"])
    reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.JSONField(required=False)

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)
        status = attrs.get("gold_submitted_status")

        if is_complete:
            if not status:
                raise serializers.ValidationError({"gold_submitted_status": "Status is mandatory"})
            
            if status == "No":
                if not attrs.get("reason"):
                    raise serializers.ValidationError({"reason": "Reason is mandatory when status is No"})
                if not attrs.get("remarks"):
                    raise serializers.ValidationError({"remarks": "Remarks are mandatory when status is No"})
            
            if status == "On-Hold":
                if not attrs.get("reason"):
                    raise serializers.ValidationError({"reason": "Reason is mandatory when status is On-Hold"})

        return attrs


class FundRefundSerializer(serializers.Serializer):
    """Fund Refund stage for Balance Transfer flow."""
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    payment_mode = serializers.ChoiceField(choices=PaymentMode.choices)
    bank_name = serializers.CharField(max_length=255)
    transaction_reference_number = serializers.CharField(max_length=255)
    fund_transferred_by = serializers.ChoiceField(choices=FundTransferredBy.choices)
    
    # Self-specific proofs
    cheque_image_url = serializers.JSONField(required=False, allow_null=True)
    cheque_image_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_empty=True,
        max_length=2,
    )
    transaction_proof_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    
    # Third-party specific proofs
    relationship = serializers.ChoiceField(choices=Relation.choices, required=False, allow_null=True)
    relationship_proof_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    
    metadata = serializers.JSONField(required=False)
    
    PAYMENT_MODE_ALIAS_MAP = {
        "CASH": PaymentMode.CASH,
        "CHEQUE": PaymentMode.CHEQUE,
        "NEFT": PaymentMode.NEFT,
        "IMPS": PaymentMode.IMPS,
        "RTGS": PaymentMode.RTGS,
        "UPI": PaymentMode.UPI,
    }
    FUND_TRANSFERRED_BY_ALIAS_MAP = {
        "SELF": FundTransferredBy.SELF,
        "THIRD_PARTY": FundTransferredBy.THIRD_PARTY,
    }
    
    @staticmethod
    def _normalize_choice(value, aliases):
        if not isinstance(value, str):
            return value
        normalized = value.strip().upper()
        return aliases.get(normalized, value)
    
    @staticmethod
    def _clean_url(url):
        if not isinstance(url, str):
            return url
        cleaned = url.strip()
        # Remove surrounding backticks if present
        if cleaned.startswith('`') and cleaned.endswith('`'):
            cleaned = cleaned[1:-1].strip()
        return cleaned if cleaned else None
        
    def to_internal_value(self, data):
        if isinstance(data, dict):
            normalized = dict(data)
            if "payment_mode" in normalized:
                normalized["payment_mode"] = self._normalize_choice(
                    normalized.get("payment_mode"), self.PAYMENT_MODE_ALIAS_MAP
                )
            if "fund_transferred_by" in normalized:
                normalized["fund_transferred_by"] = self._normalize_choice(
                    normalized.get("fund_transferred_by"), self.FUND_TRANSFERRED_BY_ALIAS_MAP
                )
            # Clean up individual URL fields (if they are strings) and list fields
            for field in ["transaction_proof_url", "relationship_proof_url"]:
                if field in normalized:
                    normalized[field] = self._clean_url(normalized[field])
            # Handle cheque_image_url (can be string or list)
            if "cheque_image_url" in normalized:
                if isinstance(normalized["cheque_image_url"], list):
                    normalized["cheque_image_url"] = [
                        self._clean_url(url) for url in normalized["cheque_image_url"]
                    ]
                else:
                    normalized["cheque_image_url"] = self._clean_url(normalized["cheque_image_url"])
            # Clean up cheque_image_urls list
            if "cheque_image_urls" in normalized and isinstance(normalized["cheque_image_urls"], list):
                normalized["cheque_image_urls"] = [
                    self._clean_url(url) for url in normalized["cheque_image_urls"]
                ]
            data = normalized
        return super().to_internal_value(data)

    def validate_cheque_image_url(self, value):
        if value is None:
            return None
        url_field = serializers.URLField()
        if isinstance(value, str):
            return url_field.run_validation(value)
        elif isinstance(value, list):
            return [url_field.run_validation(url) for url in value]
        raise serializers.ValidationError("Must be a URL or a list of URLs")

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)
        application = self.context.get("application")
        fund_by = attrs.get("fund_transferred_by")
        refund_amount = attrs.get("amount")
        ref_number = attrs.get("transaction_reference_number")
        cheque_image_url = attrs.get("cheque_image_url")
        cheque_image_urls = attrs.get("cheque_image_urls")

        if cheque_image_urls is None:
            if isinstance(cheque_image_url, list):
                attrs["cheque_image_urls"] = cheque_image_url
                if cheque_image_url:
                    attrs["cheque_image_url"] = cheque_image_url[0]
            elif cheque_image_url:
                attrs["cheque_image_urls"] = [cheque_image_url]
        elif cheque_image_urls and not cheque_image_url:
            attrs["cheque_image_url"] = cheque_image_urls[0]

        if is_complete:
            if not refund_amount or refund_amount <= 0:
                raise serializers.ValidationError({"amount": "Valid refund amount is mandatory"})
            
            if application:
                pending_amount = calculate_fund_refund_amounts(application)["pending_amount"]

                if refund_amount > pending_amount:
                    raise serializers.ValidationError({"amount": f"Refund amount cannot exceed pending amount of {pending_amount}"})

                # Check for duplicate transaction reference number locally
                if ref_number:
                    current_payload = application.stage_payload if isinstance(application.stage_payload, dict) else {}
                    existing_refunds = current_payload.get("fund_refund", [])
                    if not isinstance(existing_refunds, list):
                        existing_refunds = []
                    
                    # Also check the stage snapshot if needed
                    if not existing_refunds:
                        try:
                            from onboarding_v2.constants import ApplicationStage
                            snapshot = application.stage_snapshots.get(stage=ApplicationStage.FUND_REFUND)
                            if isinstance(snapshot.payload, list):
                                existing_refunds = snapshot.payload
                        except Exception:
                            pass
                    
                    for r in existing_refunds:
                        if (
                            isinstance(r, dict)
                            and r.get("transaction_reference_number") == ref_number
                            and r.get("status") != TransactionStatus.REJECTED
                        ):
                            raise serializers.ValidationError({"transaction_reference_number": "This transaction reference number has already been used for this application."})

            if fund_by == FundTransferredBy.THIRD_PARTY:
                if not attrs.get("relationship"):
                    raise serializers.ValidationError({"relationship": "Relationship is mandatory for third party transfer"})
                if not attrs.get("relationship_proof_url"):
                    raise serializers.ValidationError({"relationship_proof_url": "Relationship proof is mandatory for third party transfer"})

        return attrs


class ChooseCustomerSerializer(serializers.Serializer):
    """Choose Customer stage for Balance Transfer flow."""
    customer_choice = serializers.ChoiceField(choices=["Self", "Others"])
    relationship = serializers.ChoiceField(choices=Relation.choices, required=False, allow_null=True)
    metadata = serializers.JSONField(required=False)

    def validate(self, attrs):
        is_complete = self.context.get("is_complete", False)
        choice = attrs.get("customer_choice")
        relationship = attrs.get("relationship")

        if is_complete:
            if not choice:
                raise serializers.ValidationError({"customer_choice": "Selection is mandatory"})
            if choice == "Others" and not relationship:
                raise serializers.ValidationError({"relationship": "Relationship is mandatory when choice is Others"})

        return attrs


class CorrectionRaiseSerializer(serializers.Serializer):
    stage = serializers.ChoiceField(choices=ApplicationStage.choices)
    field_name = serializers.CharField(max_length=255)
    image_id = serializers.CharField(max_length=128, required=False, allow_null=True)
    payload = serializers.JSONField(required=False)


class RHActionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["APPROVE", "REJECT", "CORRECTION"], required=False)
    action = serializers.ChoiceField(choices=["APPROVE", "REJECT", "CORRECTION"], required=False)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        status = attrs.get("status")
        action = attrs.get("action")
        if not status and not action:
            raise serializers.ValidationError("Either 'status' or 'action' field is required.")
        if not status:
            attrs["status"] = action
        return attrs


class CorrectionOnboardingListSerializer(serializers.ModelSerializer):
    """Read serializer for listing CorrectionOnboarding records."""
    application_id = serializers.CharField(source="application.application_id", read_only=True)

    class Meta:
        model = CorrectionOnboarding
        fields = [
            "id",
            "application_id",
            "stage",
            "field_name",
            "image_id",
            "payload",
            "status",
            "created_at",
            "modified_at",
        ]
