from rest_framework import serializers
from urllib.parse import urlparse
import mimetypes

from onboarding_v2.models import ApplicationStageSnapshot, ApplicationV2
from onboarding_v2.serializers.loan_punch import SingleLoanPunchSerializer
from onboarding_v2.storage import generate_presigned_get
from utils.envSetup import environment


def _storage_bucket_candidates():
    return {
        bucket
        for bucket in (
            getattr(environment, "STORAGE_BUCKET_NAME", None),
            getattr(environment, "DEV_STORAGE_BUCKET_NAME", None),
            getattr(environment, "PROD_STORAGE_BUCKET_NAME", None),
        )
        if bucket
    }


def _looks_like_storage_url(file_url: str) -> bool:
    if not file_url or not isinstance(file_url, str):
        return False

    parsed = urlparse(file_url)
    endpoint = (getattr(environment, "STORAGE_ENDPOINT", "") or "").strip().lower()

    # Non-URL values may be stored as object names; treat them as storage objects.
    if not parsed.scheme and not parsed.netloc:
        return True

    netloc = parsed.netloc.lower()
    if endpoint and netloc == endpoint:
        return True

    path_parts = parsed.path.lstrip("/").split("/", 1)
    if path_parts and path_parts[0] in _storage_bucket_candidates():
        return True

    return False


def _safe_presign_file_url(file_url):
    if not isinstance(file_url, str):
        return file_url

    if not _looks_like_storage_url(file_url):
        return file_url

    parsed = urlparse(file_url)
    source_for_mime = parsed.path or file_url
    guessed_mime, _ = mimetypes.guess_type(source_for_mime)
    response_headers = {"response-content-disposition": "inline"}
    if guessed_mime:
        response_headers["response-content-type"] = guessed_mime

    try:
        presigned = generate_presigned_get(
            file_url=file_url,
            response_headers=response_headers,
        )
        return presigned.get("get_url") or file_url
    except Exception:
        return file_url


def _presign_payload_file_urls(value):
    if isinstance(value, list):
        return [_presign_payload_file_urls(item) for item in value]

    if isinstance(value, dict):
        transformed = {}
        for key, item in value.items():
            if (
                isinstance(key, str)
                and isinstance(item, str)
                and (key == "file_url" or key.endswith("_url"))
            ):
                transformed[key] = _safe_presign_file_url(item)
            else:
                transformed[key] = _presign_payload_file_urls(item)
        return transformed

    return value


class ApplicationSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStageSnapshot
        fields = ["stage", "payload", "is_complete", "modified_at", "created_at"]


class ApplicationStateSerializer(serializers.ModelSerializer):
    snapshots = serializers.SerializerMethodField()
    customer_id = serializers.SerializerMethodField()
    lead_code = serializers.SerializerMethodField()
    lead_amount = serializers.SerializerMethodField()
    processing_fee_info = serializers.SerializerMethodField()
    punched_loans = SingleLoanPunchSerializer(many=True, read_only=True)
    bureau_report_link = serializers.SerializerMethodField()
    punched_by_name = serializers.CharField(source="punched_by.get_full_name", read_only=True)
    punched_by_employee_id = serializers.CharField(source="punched_by.employee_id", read_only=True, allow_null=True)
    assigned_rh_name = serializers.CharField(source="assigned_rh.get_full_name", read_only=True)

    # --- New customer detail fields ---
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone_no = serializers.SerializerMethodField()
    lead_id = serializers.SerializerMethodField()
    lead_added_on = serializers.SerializerMethodField()
    requested_amount = serializers.SerializerMethodField()
    dob = serializers.SerializerMethodField()
    dob_from_pan = serializers.SerializerMethodField()
    place_of_birth = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    alternate_no = serializers.SerializerMethodField()
    father_name = serializers.SerializerMethodField()
    mother_name = serializers.SerializerMethodField()
    marital_status = serializers.SerializerMethodField()
    profession = serializers.SerializerMethodField()
    occupation = serializers.SerializerMethodField()
    profile_pic = serializers.SerializerMethodField()
    income_source = serializers.SerializerMethodField()
    annual_income = serializers.SerializerMethodField()
    net_income_per_month = serializers.SerializerMethodField()
    net_worth = serializers.SerializerMethodField()
    religion = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationV2
        fields = [
            "application_id",
            "customer_id",
            "lead_code",
            "lead_amount",
            "lending_partner",
            "status",
            "van_number",
            "stage",
            "pre_screen_completion",
            "post_screen_completion",
            "saas_status",
            "punched_by",
            "punched_by_name",
            "punched_by_employee_id",
            "assigned_rh",
            "assigned_rh_name",
            "bureau_score",
            "score_color",
            "bureau_decision",
            "bureau_report_link",
            "processing_fee",
            "processing_fee_info",
            "snapshots",
            "punched_loans",
            # New fields
            "name",
            "email",
            "phone_no",
            "lead_id",
            "lead_added_on",
            "requested_amount",
            "dob",
            "dob_from_pan",
            "place_of_birth",
            "gender",
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
        ]

    # --- Helper to get stage snapshot payload ---
    def _get_snapshot_payload(self, obj, stage_name):
        """Get the payload dict from a stage snapshot."""
        try:
            snapshot = obj.stage_snapshots.get(stage=stage_name)
            payload = snapshot.payload
            return payload if isinstance(payload, dict) else {}
        except ApplicationStageSnapshot.DoesNotExist:
            return {}

    # --- Lead-based fields ---
    def get_customer_id(self, obj):
        lead = getattr(obj, "lead", None)
        return getattr(lead, "customer_id", "") if lead else ""

    def get_lead_code(self, obj):
        lead = getattr(obj, "lead", None)
        return getattr(lead, "lead_code", "") if lead else ""

    def get_lead_amount(self, obj):
        lead = getattr(obj, "lead", None)
        return getattr(lead, "amount", None) if lead else None

    def get_name(self, obj):
        lead = getattr(obj, "lead", None)
        return getattr(lead, "customer_name", "") if lead else ""

    def get_email(self, obj):
        lead = getattr(obj, "lead", None)
        return getattr(lead, "email_address", None) if lead else None

    def get_phone_no(self, obj):
        lead = getattr(obj, "lead", None)
        return getattr(lead, "contact_number", "") if lead else ""

    def get_lead_id(self, obj):
        lead = getattr(obj, "lead", None)
        return str(lead.id) if lead else None

    def get_lead_added_on(self, obj):
        lead = getattr(obj, "lead", None)
        return getattr(lead, "created_at", None) if lead else None

    def get_requested_amount(self, obj):
        lead = getattr(obj, "lead", None)
        amount = getattr(lead, "amount", None) if lead else None
        return str(amount) if amount is not None else None

    # --- DOB fields ---
    def get_dob(self, obj):
        lead = getattr(obj, "lead", None)
        lead_dob = getattr(lead, "dob", None) if lead else None
        if lead_dob:
            return str(lead_dob)
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("dob") or basic.get("date_of_birth")

    def get_dob_from_pan(self, obj):
        pan = self._get_snapshot_payload(obj, "PAN")
        return pan.get("dob_as_per_pan") or pan.get("dob")

    # --- Snapshot-based fields ---
    def get_place_of_birth(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("place_of_birth")

    def get_gender(self, obj):
        lead = getattr(obj, "lead", None)
        lead_gender = getattr(lead, "gender", None) if lead else None
        if lead_gender:
            return lead_gender
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("gender")

    def get_alternate_no(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("alternate_no") or basic.get("alternate_number") or basic.get("alternate_contact_number")

    def get_father_name(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("father_name") or basic.get("fathers_name")

    def get_mother_name(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("mother_name") or basic.get("mothers_name")

    def get_marital_status(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("marital_status")

    def get_profession(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        if basic.get("profession"):
            return basic.get("profession")
        return getattr(obj, "applicant_profession", None)

    def get_occupation(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        if basic.get("occupation"):
            return basic.get("occupation")
        return getattr(obj, "occupation", None)

    def get_profile_pic(self, obj):
        selfie = self._get_snapshot_payload(obj, "SELFIE")
        url = selfie.get("file_url") or selfie.get("image_url") or selfie.get("selfie_url")
        if url:
            return _safe_presign_file_url(url)
        return None

    def get_income_source(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        if basic.get("income_source"):
            return basic.get("income_source")
        return getattr(obj, "income_source", None)

    def get_annual_income(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("annual_income") or basic.get("annual_income_family")

    def get_net_income_per_month(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("net_income_per_month") or basic.get("monthly_income")

    def get_net_worth(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("net_worth")

    def get_religion(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        return basic.get("religion")

    def get_category(self, obj):
        basic = self._get_snapshot_payload(obj, "BASIC")
        if basic.get("category"):
            return basic.get("category")
        return getattr(obj, "caste", None)

    # --- Existing fields ---
    def get_bureau_report_link(self, obj):
        if obj.bureau_report_link:
            return _safe_presign_file_url(obj.bureau_report_link)
        return None

    def get_snapshots(self, obj):
        filter_stages = self.context.get("filter_stages")
        snaps = obj.stage_snapshots.all().order_by("stage", "-modified_at")
        
        if filter_stages:
            snaps = snaps.filter(stage__in=filter_stages)
            
        serialized = ApplicationSnapshotSerializer(snaps, many=True).data
        return [
            {
                **snapshot,
                "payload": _presign_payload_file_urls(snapshot.get("payload")),
            }
            for snapshot in serialized
        ]

    def get_processing_fee_info(self, obj):
        from decimal import Decimal
        from onboarding_v2.serializers import _pf_rate_for_score, _waiver_limit_for_score
        bureau_score = obj.bureau_score
        lead = getattr(obj, "lead", None)
        loan_amount = Decimal(str(getattr(lead, "amount", None) or 0))
        pf_rate = _pf_rate_for_score(bureau_score)
        processing_fee = (loan_amount * pf_rate / Decimal("100")).quantize(Decimal("0.01"))
        max_waiver_pct = _waiver_limit_for_score(bureau_score) if bureau_score is not None else None
        return {
            "processing_fee": str(processing_fee),
            "pf_rate_percent": str(pf_rate),
            "max_waiver_percent": str(max_waiver_pct) if max_waiver_pct is not None else None,
            "bureau_score": bureau_score,
        }

