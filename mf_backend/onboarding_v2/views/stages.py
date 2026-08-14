import logging
import requests
import uuid
import re
from decimal import Decimal, ROUND_DOWN

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from onboarding_v2.authentication import SaasWebhookAuthentication
from middlewares.auth import CustomPermission

from onboarding_v2.signzy_experian import run_experian_bureau_check
from utils.responseHandler import HttpResponse
from utility.error_handler import HttpErrors
from utils.helper import price_of_gold_22_karates
from onboarding_v2.constants import (
    ApplicationStage,
    FRESH_LOAN_STAGES,
    FRESH_GOLD_LOAN_STAGES,
    CO_LENDING_STAGES,
    SELF_LENDING_STAGES,
    LoanSubCategory,
    LeadType,
    ApplicationStatus,
    ProductSubCategory,
)
from onboarding_v2.models import (
    ApplicationStageSnapshot,
    ApplicationV2,
    CorrectionOnboarding,
    Customers,
)
from onboarding_v2.helpers.persistence_helpers import (
    annotate_customer_visit_ids,
    annotate_pledge_ids,
    annotate_poa_ids,
    persist_additional,
    persist_addresses,
    persist_basic,
    persist_bank,
    persist_customer_visit,
    persist_documents,
    persist_eligibility,
    persist_gold,
    persist_loan,
    persist_self_declaration,
    persist_charges,
    normalize_bt_waiver_payload,
    persist_pan,
    persist_personal,
    persist_pledge_card,
    persist_selfie,
    persist_waiver,
    persist_amount_transferred,
    persist_gold_received,
    persist_gold_submitted,
    persist_choose_customer,
    persist_fund_refund,
    persist_loan_range_selection,
    persist_product_selection,
)
from onboarding_v2.serializers import (
    AdditionalDetailsSerializer,
    AddressSecondarySerializer,
    AddressStageSerializer,
    ApplicationV2Serializer,
    BankDetailsSerializer,
    BTCustomerVisitSerializer,
    CustomerDefaulterCheckSerializer,
    DocumentUploadSerializer,
    GoldPacketSerializer,
    LoanDetailsSerializer,
    PanStageSerializer,
    PersonalDetailsSerializer,
    PledgeCardSerializer,
    SelfieStageSerializer,
    StageUpdateSerializer,
    BasicStageSerializer,
    CustomerVisitSerializer,
    EligibilityStageSerializer,
    BTAdditionalDetailsSerializer,
    BTWaiverSerializer,
    AmountTransferredSerializer,
    GoldReceivedSerializer,
    GoldSubmittedSerializer,
    ChooseCustomerSerializer,
    FundRefundSerializer,
    SelfDeclarationSerializer,
    ChargesDetailsSerializer,
    CorrectionRaiseSerializer,
    CorrectionOnboardingListSerializer,
    WaiverSerializer,
    RHActionSerializer,
    LoanRangeSelectionSerializer,
    ProductSelectionSerializer,
    LendingPartnerBankSerializer,
)
from onboarding_v2.helpers.stage_helpers import save_stage_snapshot, update_application_progress
from onboarding_v2.serializers.state import ApplicationStateSerializer
from onboarding_v2.helpers.fund_refund_helpers import calculate_fund_refund_amounts
from onboarding_v2.helpers.view_helpers import merge_gold_payload, merge_payload
from onboarding_v2.services import sync_lead_status


logger = logging.getLogger(__name__)


def _customer_phone_lookup_values(contact_number):
    values = []

    def add(value):
        if value is None:
            return
        value = str(value).strip()
        if value and value not in values:
            values.append(value)

    add(contact_number)
    digits = re.sub(r"\D", "", str(contact_number or ""))
    if not digits:
        return values

    add(digits)
    if len(digits) == 10:
        add(f"+91{digits}")
        add(f"91{digits}")
    elif digits.startswith("91") and len(digits) == 12:
        national_digits = digits[2:]
        add(national_digits)
        add(f"+{digits}")
    elif digits.startswith("0") and len(digits) == 11:
        national_digits = digits[1:]
        add(national_digits)
        add(f"+91{national_digits}")
        add(f"91{national_digits}")

    return values


def _build_customer_defaulter_query(pan_number, contact_number):
    query = Q()
    pan_number = (pan_number or "").strip().upper()
    if pan_number:
        query |= Q(pan_number__iexact=pan_number)

    for phone in _customer_phone_lookup_values(contact_number):
        query |= Q(phone_number=phone)

    digits = re.sub(r"\D", "", str(contact_number or ""))
    if len(digits) >= 10:
        query |= Q(phone_number__endswith=digits[-10:])

    return query


class StageUpdateView(APIView):
    """
    Save or complete a stage payload. Mobile clients can call this with stage + payload + is_complete.
    """
    authentication_classes = [OAuth2Authentication, SaasWebhookAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = []

    def post(self, request, application_id):
        try:
            try:
                application = ApplicationV2.objects.get(application_id=application_id)
            except ApplicationV2.DoesNotExist:
                return HttpResponse.BadRequest("Application not found")
            logger.info("Stage update request | app=%s payload=%s", application_id, request.data)
            logger.info(
                "Stage update start | app=%s stage=%s user=%s",
                application_id,
                request.data.get("stage"),
                getattr(request.user, "id", None),
            )

            serializer = StageUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            stage = serializer.validated_data["stage"]
            payload = serializer.validated_data["payload"]
            is_complete = serializer.validated_data.get("is_complete", False)

            # Validate per-stage payload
            stage_serializer_cls = {
                ApplicationStage.PAN: PanStageSerializer,
                ApplicationStage.LENDING_PARTNER_BANK: LendingPartnerBankSerializer,
                ApplicationStage.LOAN_RANGE_SELECTION: LoanRangeSelectionSerializer,
                ApplicationStage.PRODUCT_SELECTION: ProductSelectionSerializer,
                ApplicationStage.SELF_DECLARATION: SelfDeclarationSerializer,
                ApplicationStage.BASIC: BasicStageSerializer,
                ApplicationStage.ADDRESS: AddressStageSerializer,
                ApplicationStage.ELIGIBILITY: EligibilityStageSerializer,
                ApplicationStage.DOCUMENTS: DocumentUploadSerializer,
                ApplicationStage.PERSONAL: PersonalDetailsSerializer,
                ApplicationStage.ADDRESS_SECONDARY: AddressSecondarySerializer,
                ApplicationStage.GOLD: GoldPacketSerializer,
                ApplicationStage.LOAN: LoanDetailsSerializer,
                ApplicationStage.PLEDGE_CARD: PledgeCardSerializer,
                ApplicationStage.BANK: BankDetailsSerializer,
                ApplicationStage.SELFIE: SelfieStageSerializer,
                ApplicationStage.CUSTOMER_VISIT: BTCustomerVisitSerializer if application.loan_type == LeadType.BALANCE_TRANSFER else CustomerVisitSerializer,
                ApplicationStage.ADDITIONAL: BTAdditionalDetailsSerializer if application.loan_type == LeadType.BALANCE_TRANSFER else AdditionalDetailsSerializer,
                ApplicationStage.CHARGES: ChargesDetailsSerializer,
                ApplicationStage.WAIVER: BTWaiverSerializer if application.loan_type == LeadType.BALANCE_TRANSFER else WaiverSerializer,
                ApplicationStage.AMOUNT_TRANSFERRED: AmountTransferredSerializer,
                ApplicationStage.GOLD_RECEIVED: GoldReceivedSerializer,
                ApplicationStage.GOLD_SUBMITTED: GoldSubmittedSerializer,
                ApplicationStage.CHOOSE_CUSTOMER: ChooseCustomerSerializer,
                ApplicationStage.FUND_REFUND: FundRefundSerializer,
            }.get(stage)

            if stage_serializer_cls:
                payload_for_validation = payload
                if isinstance(payload, dict) and request.FILES:
                    payload_for_validation = {**payload, **request.FILES}
                if stage == ApplicationStage.PAN and isinstance(payload_for_validation, dict):
                    payload_for_validation.setdefault("contact_number", application.lead.contact_number)
                stage_ser = stage_serializer_cls(
                    data=payload_for_validation, 
                    many=stage == ApplicationStage.DOCUMENTS,
                    context={
                        "application": application,
                        "is_complete": is_complete,
                        "stage": stage,
                        "request": request,
                    }
                )
                if not stage_ser.is_valid():
                    errors = stage_ser.errors
                    if isinstance(errors, list) and len(errors) > 0:
                        # Flatten list errors (common in many=True serializers)
                        for err in errors:
                            if isinstance(err, dict) and err:
                                first_key = next(iter(err))
                                first_val = err[first_key]
                                if isinstance(first_val, list):
                                    first_val = first_val[0]
                                return HttpResponse.BadRequest(f"{first_key}: {first_val}")
                    elif isinstance(errors, dict):
                        if "non_field_errors" in errors:
                            return HttpResponse.BadRequest(errors["non_field_errors"][0])
                        # Handle other dict errors
                        first_key = next(iter(errors))
                        first_val = errors[first_key]
                        if isinstance(first_val, list):
                            first_val = first_val[0]
                        return HttpResponse.BadRequest(f"{first_key}: {first_val}")
                    return HttpResponse.BadRequest(errors)
                # Use serializer output to coerce datatypes (e.g., dates) into JSON-serializable primitives
                payload = stage_ser.data

            if stage == ApplicationStage.DOCUMENTS and isinstance(payload, list):
                try:
                    existing_snapshot = application.stage_snapshots.get(stage=stage)
                    existing_docs = (
                        existing_snapshot.payload if isinstance(existing_snapshot.payload, list) else []
                    )
                except ApplicationStageSnapshot.DoesNotExist:
                    existing_docs = []

                # Merge by file_url (if present) to avoid duplicates, otherwise keep all
                merged = {}
                for item in existing_docs:
                    if not isinstance(item, dict):
                        continue
                    key = item.get("file_url") or str(uuid.uuid4())  # Use file_url as key if available
                    merged[key] = item
                for item in payload:
                    if not isinstance(item, dict):
                        continue
                    key = item.get("file_url") or str(uuid.uuid4())
                    merged[key] = item
                payload = list(merged.values())

            if stage == ApplicationStage.GOLD and isinstance(payload, dict):
                try:
                    existing_snapshot = application.stage_snapshots.get(stage=stage)
                    existing_payload = (
                        existing_snapshot.payload if isinstance(existing_snapshot.payload, dict) else {}
                    )
                except ApplicationStageSnapshot.DoesNotExist:
                    existing_payload = {}
                if not existing_payload or not existing_payload.get("items"):
                    stage_payload = application.stage_payload if isinstance(application.stage_payload, dict) else {}
                    if stage_payload.get("items"):
                        existing_payload = stage_payload
                # Merge with the raw incoming payload so optional fields (like item_index) aren't dropped
                raw_payload = request.data.get("payload") if isinstance(request.data, dict) else None
                if isinstance(raw_payload, dict):
                    payload = merge_gold_payload(existing_payload, raw_payload)
                else:
                    payload = merge_gold_payload(existing_payload, payload)
                try:
                    rate_22 = Decimal(str(price_of_gold_22_karates()))
                except Exception:
                    rate_22 = Decimal("0")
                ltv_rate_22 = (rate_22 * Decimal("0.75")).quantize(Decimal("1"), rounding=ROUND_DOWN)
                items = list(payload.get("items") or [])
                def _to_dec(v):
                    if v in (None, ""):
                        return Decimal("0")
                    try:
                        return Decimal(str(v))
                    except Exception:
                        return Decimal("0")
                def _karat(p):
                    if p in (None, ""):
                        return Decimal("22")
                    s = "".join(ch for ch in str(p) if ch.isdigit())
                    if not s:
                        return Decimal("22")
                    try:
                        return Decimal(s)
                    except Exception:
                        return Decimal("22")
                updated_items = []
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    k = _karat(it.get("purity"))
                    gross_w = _to_dec(it.get("gross_weight"))
                    stone_w = _to_dec(it.get("stone_weight"))
                    impurity_w = _to_dec(it.get("impurity_weight") if it.get("impurity_weight") is not None else it.get("impurity_deducted"))
                    if gross_w and (stone_w or impurity_w):
                        net_w = gross_w - stone_w - impurity_w
                        if net_w < 0:
                            net_w = Decimal("0")
                        net_w = net_w.quantize(Decimal("0.01"))
                    else:
                        net_w = _to_dec(it.get("net_weight")).quantize(Decimal("0.01"))
                    provided_rate = _to_dec(it.get("actual_gold_rate"))
                    actual_rate = provided_rate if provided_rate > 0 else (ltv_rate_22 / Decimal("22") * k).quantize(Decimal("0.01"))
                    naw = (net_w * k / Decimal("22")).quantize(Decimal("0.01"))
                    gv = (gross_w * actual_rate).quantize(Decimal("0.01"))
                    nv = (net_w * actual_rate).quantize(Decimal("0.01"))
                    per_carat_rate = (actual_rate / (k if k > 0 else Decimal("22"))).quantize(Decimal("0.01"))
                    rate_22_norm = (per_carat_rate * Decimal("22")).quantize(Decimal("0.01"))
                    nav = (naw * rate_22_norm).quantize(Decimal("0.01"))
                    percent_gold = Decimal("0")
                    if gross_w > 0:
                        percent_gold = ((net_w / gross_w) * Decimal("100")).quantize(Decimal("0.01"))
                    it = dict(it)
                    it["net_weight"] = str(net_w)
                    it["actual_gold_rate"] = str(actual_rate)
                    it["net_adjusted_weight"] = str(naw)
                    it["gross_value"] = str(gv)
                    it["net_adjusted_value"] = str(nv)
                    it["net_value"] = str(nv)
                    it["percent_of_gold"] = str(percent_gold)
                    updated_items.append(it)
                payload["items"] = updated_items
                gw_sum = Decimal("0")
                gv_sum = Decimal("0")
                naw_sum = Decimal("0")
                nav_sum = Decimal("0")
                for it in updated_items:
                    gw_sum += _to_dec(it.get("gross_weight"))
                    gv_sum += _to_dec(it.get("gross_value"))
                    naw_sum += _to_dec(it.get("net_adjusted_weight"))
                    nav_sum += _to_dec(it.get("net_adjusted_value"))
                payload["gross_weight"] = str(gw_sum.quantize(Decimal("0.01")))
                payload["gross_value"] = str(gv_sum.quantize(Decimal("0.01")))
                payload["net_adjusted_weight"] = str(naw_sum.quantize(Decimal("0.01")))
                payload["net_adjusted_value"] = str(nav_sum.quantize(Decimal("0.01")))
            elif isinstance(payload, dict) and stage not in (ApplicationStage.DOCUMENTS, ApplicationStage.FUND_REFUND):
                try:
                    existing_snapshot = application.stage_snapshots.get(stage=stage)
                    existing_payload = (
                        existing_snapshot.payload if isinstance(existing_snapshot.payload, dict) else {}
                    )
                except ApplicationStageSnapshot.DoesNotExist:
                    existing_payload = {}
                payload = merge_payload(existing_payload, payload)

            if stage in (ApplicationStage.ADDRESS, ApplicationStage.ADDRESS_SECONDARY):
                annotate_poa_ids(payload)
            elif stage == ApplicationStage.PLEDGE_CARD:
                annotate_pledge_ids(payload)
            elif stage == ApplicationStage.CUSTOMER_VISIT:
                annotate_customer_visit_ids(payload)

            # Persist stage-specific entities if completing
            pan_info = None
            if is_complete:
                if stage == ApplicationStage.PAN:
                    try:
                        pan_info = persist_pan(application, payload)
                    except ValueError as ve:
                        return HttpResponse.BadRequest(str(ve))
                elif stage == ApplicationStage.LENDING_PARTNER_BANK:
                    from onboarding_v2.helpers.persistence_helpers import persist_lending_partner_bank
                    payload = persist_lending_partner_bank(application, payload)
                elif stage == ApplicationStage.LOAN_RANGE_SELECTION:
                    persist_loan_range_selection(application, payload)
                elif stage == ApplicationStage.PRODUCT_SELECTION:
                    persist_product_selection(application, payload)
                elif stage == ApplicationStage.SELF_DECLARATION:
                    persist_self_declaration(application, payload)
                elif stage == ApplicationStage.ADDRESS:
                    persist_addresses(application, payload)
                elif stage == ApplicationStage.BASIC:
                    persist_basic(application, payload)
                elif stage == ApplicationStage.DOCUMENTS:
                    persist_documents(application, payload)
                elif stage == ApplicationStage.ELIGIBILITY:
                    persist_eligibility(application, payload)
                elif stage == ApplicationStage.PERSONAL:
                    persist_personal(application, payload)
                elif stage == ApplicationStage.ADDRESS_SECONDARY:
                    persist_addresses(application, payload, secondary=True)
                elif stage == ApplicationStage.GOLD:
                    persist_gold(application, payload)
                elif stage == ApplicationStage.LOAN:
                    persist_loan(application, payload)
                elif stage == ApplicationStage.PLEDGE_CARD:
                    persist_pledge_card(application, payload)
                elif stage == ApplicationStage.BANK:
                    persist_bank(application, payload)
                elif stage == ApplicationStage.SELFIE:
                    persist_selfie(application, payload)
                elif stage == ApplicationStage.CUSTOMER_VISIT:
                    persist_customer_visit(application, payload)
                elif stage == ApplicationStage.ADDITIONAL:
                    persist_additional(application, payload)
                elif stage == ApplicationStage.CHARGES:
                    persist_charges(application, payload)
                elif stage == ApplicationStage.WAIVER:
                    if application.loan_type == LeadType.BALANCE_TRANSFER:
                        payload = normalize_bt_waiver_payload(payload)
                    persist_waiver(application, payload)
                elif stage == ApplicationStage.AMOUNT_TRANSFERRED:
                    persist_amount_transferred(application, payload)
                elif stage == ApplicationStage.GOLD_RECEIVED:
                    persist_gold_received(application, payload)
                elif stage == ApplicationStage.GOLD_SUBMITTED:
                    persist_gold_submitted(application, payload)
                elif stage == ApplicationStage.CHOOSE_CUSTOMER:
                    persist_choose_customer(application, payload)
                elif stage == ApplicationStage.FUND_REFUND:
                    try:
                        payload = persist_fund_refund(application, payload)
                    except ValueError as ve:
                        return HttpResponse.BadRequest(str(ve))

            snapshot = save_stage_snapshot(application, stage, payload, is_complete, user=request.user)
            logger.info(
                "Stage snapshot saved | app=%s stage=%s complete=%s",
                application_id,
                stage,
                is_complete,
            )

            if is_complete:
                update_application_progress(application, stage, is_complete, payload, user=request.user)

            response_payload = {
                "application": ApplicationV2Serializer(application).data,
                "snapshot": {
                    "stage": snapshot.stage,
                    "is_complete": snapshot.is_complete,
                    "payload": snapshot.payload,
                },
                **(
                    {"message": pan_info.get("message"), "detail": pan_info.get("detail")}
                    if stage == ApplicationStage.PAN and pan_info
                    else {}
                ),
            }
            logger.info("Stage update response | app=%s response=%s", application_id, response_payload)
            return HttpResponse.Success(response_payload)
        except Exception as exc:
            logger.exception("Stage update failed | app=%s", application_id)
            from onboarding_v2 import views as views_module

            views_module.notify_app_step_error(
                application_id, f"STAGE_{request.data.get('stage')}", str(exc), payload=request.data
            )
            return HttpErrors.InternalServerError("Stage update failed")


class EligibilityCheckView(APIView):

    def post(self, request, application_id):
        try:
            try:
                application = ApplicationV2.objects.get(application_id=application_id)
                return run_experian_bureau_check(application)
            except ApplicationV2.DoesNotExist:
                return HttpResponse.BadRequest("Application not found")
        except ValueError as ve:
            return HttpErrors.InternalServerError("Failed to check eligibility")



class SubmitApplicationView(APIView):
    def post(self, request, application_id):
        logger.info("Submit application request | app=%s payload=%s", application_id, request.data)
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        # Check for fresh or balance transfer loan type
        if getattr(request.user, "is_authenticated", False):
            application._status_changed_by = request.user

        current_stage_str = request.data.get("current_stage")
        if application.loan_type in [
            LeadType.FRESH,
            LeadType.BALANCE_TRANSFER,
            LeadType.CO_LENDING,
            LeadType.SELF_LENDING,
        ] and current_stage_str:
            try:
                current_stage = ApplicationStage(current_stage_str)
            except ValueError:
                return HttpResponse.BadRequest(f"Invalid current_stage: {current_stage_str}")

            if application.loan_type == LeadType.FRESH:
                stages = FRESH_LOAN_STAGES
                if application.lead.product_subcategory == ProductSubCategory.GOLD_LOAN:
                    stages = FRESH_GOLD_LOAN_STAGES
            elif application.loan_type == LeadType.CO_LENDING:
                stages = CO_LENDING_STAGES
            elif application.loan_type == LeadType.BALANCE_TRANSFER:
                from onboarding_v2.constants import BT_LOAN_STAGES
                stages = BT_LOAN_STAGES
            else:
                stages = SELF_LENDING_STAGES

            try:
                current_stage_index = [s[0] for s in stages].index(current_stage)
            except ValueError:
                return HttpResponse.BadRequest(f"Invalid stage for {application.loan_type}: {current_stage}")

            # For submission, we only require stages up to the current stage to be completed
            required_stages = [s[0] for s in stages[:current_stage_index + 1]]
            completed_stages = set(
                application.stage_snapshots.filter(
                    stage__in=required_stages,
                    is_complete=True,
                ).values_list("stage", flat=True)
            )
            missing_stages = [stage for stage in required_stages if stage not in completed_stages]
            if missing_stages:
                return HttpResponse.BadRequest(
                    {
                        "message": "Please complete all required stages before submitting.",
                        "missing_stages": missing_stages,
                    }
                )

            # Determine if this is a submission stage
            is_submission_stage = False
            if application.loan_type == LeadType.BALANCE_TRANSFER:
                # For BT, submission happens at WAIVER stage or at the very end
                if current_stage == ApplicationStage.WAIVER or current_stage_index == len(stages) - 1:
                    is_submission_stage = True
            elif current_stage_index == len(stages) - 1:
                is_submission_stage = True

            if not is_submission_stage:
                next_stage, completion_percentage = stages[current_stage_index + 1]
                application.completion_percentage = completion_percentage
                application.save()
                return HttpResponse.Success({
                    "application": ApplicationV2Serializer(application).data,
                    "message": f"Stage updated to {next_stage}. Completion: {completion_percentage}%",
                    "next_stage": next_stage,
                    "completion_percentage": completion_percentage,
                })
            else:
                # Final stage
                if not application.submitted_at:
                    application.submitted_at = timezone.now()

                save_stage_snapshot(application, ApplicationStage.SUBMITTED, {}, True, user=request.user)

                if application.loan_type == LeadType.CO_LENDING:
                    # Final stage for co-lending loan, submit for pre-screening
                    logger.info("SubmitApplicationView | Final stage submission for co-lending app=%s loan_type=%s", application.application_id, application.loan_type)
                    application.pre_screen_completion = 100
                    application.status = ApplicationStatus.SENT_FOR_PRE_SCREENING
                    application.stage = ApplicationStage.SUBMITTED
                    application.save(update_fields=["pre_screen_completion", "status", "stage", "modified_at"])
                    sync_lead_status(application, ApplicationStatus.SENT_FOR_PRE_SCREENING)
                    from onboarding_v2.helpers import saas_helpers
                    logger.info("SubmitApplicationView | Calling enqueue_pre_screen for app=%s", application.application_id)
                    saas_helpers.enqueue_pre_screen(application)
                    logger.info("SubmitApplicationView | enqueue_pre_screen completed for app=%s", application.application_id)
                    return HttpResponse.Success({
                        "application": ApplicationV2Serializer(application).data,
                        "message": "Application submitted for pre-screening.",
                        "completion_percentage": 100,
                    })
                elif application.loan_type == LeadType.FRESH:
                    # Final stage for fresh loan, submit for punching
                    application.pre_screen_completion = 100
                    application.status = ApplicationStatus.PUNCHING_PENDING
                    application.stage = ApplicationStage.SUBMITTED
                    application.save(update_fields=["pre_screen_completion", "status", "stage", "submitted_at", "modified_at"])
                    sync_lead_status(application, ApplicationStatus.PUNCHING_PENDING)
                    return HttpResponse.Success({
                        "application": ApplicationV2Serializer(application).data,
                        "message": "Application submitted for punching.",
                        "completion_percentage": 100,
                    })
                elif application.loan_type == LeadType.BALANCE_TRANSFER:
                    # Final stage for balance transfer, submit to underwriting
                    from onboarding_v2.helpers import saas_helpers
                    
                    if application.status in [ApplicationStatus.CORRECTION_RAISED_BY_UNDERWRITING, ApplicationStatus.CORRECTION_RAISED_BY_RH]:
                        # Mark existing pending corrections as resolved
                        CorrectionOnboarding.objects.filter(
                            application=application,
                            status=CorrectionOnboarding.Status.PENDING
                        ).update(status=CorrectionOnboarding.Status.RESOLVED)
                        result = saas_helpers.enqueue_bt_update(application)
                    else:
                        result = saas_helpers.enqueue_bt_onboard(application)
                    
                    if isinstance(result, dict) and "Onboard data already exist" in (result.get("message") or ""):
                        return HttpResponse.BadRequest({
                            "message": result.get("message"),
                            "code": result.get("code"),
                            "status": result.get("status")
                        })
                    
                    # Note: status is updated inside the tasks (save_onboard_details_task / update_onboard_details_task)
                    # but we also set it here for immediate response consistency if needed.
                    # Actually, the user wants it to be SUBMITTED_TO_UNDERWRITING on success.
                    # The tasks already do this.
                    
                    application.post_screen_completion = 100
                    application.stage = ApplicationStage.SUBMITTED
                    application.save(update_fields=["post_screen_completion", "stage", "submitted_at", "modified_at"])
                    
                    return HttpResponse.Success({
                        "application": ApplicationV2Serializer(application).data,
                        "message": "Application submitted to underwriting.",
                        "completion_percentage": 100,
                        "status": application.status
                    })
                else:
                    from onboarding_v2 import views as views_module

                    try:
                        views_module.enqueue_pre_screen(application)
                    except ValueError as exc:
                        logger.warning(
                            "Self Lending pre-screen validation failed | app=%s error=%s",
                            application.application_id,
                            exc,
                        )
                        return HttpResponse.BadRequest(str(exc))
                    application.post_screen_completion = 100
                    application.status = ApplicationStatus.SENT_FOR_PRE_SCREENING
                    application.stage = ApplicationStage.SUBMITTED
                    application.save(
                        update_fields=[
                            "post_screen_completion",
                            "status",
                            "stage",
                            "submitted_at",
                            "modified_at",
                        ]
                    )
                    sync_lead_status(
                        application, ApplicationStatus.SENT_FOR_PRE_SCREENING
                    )
                    return HttpResponse.Success(
                        {
                            "application": ApplicationV2Serializer(application).data,
                            "message": "Self Lending application submitted for pre-screening.",
                            "completion_percentage": 100,
                            "status": application.status,
                        }
                    )

        # Original submission logic for other loan types
        if application.loan_type == LeadType.BALANCE_TRANSFER and application.status == ApplicationStatus.ESIGN_COMPLETED:
            if getattr(request.user, "is_authenticated", False):
                application._status_changed_by = request.user
            if not application.submitted_at:
                application.submitted_at = timezone.now()
            save_stage_snapshot(application, ApplicationStage.SUBMITTED, {}, True, user=request.user)
            application.status = ApplicationStatus.RH_APPROVAL_PENDING
            application.stage = ApplicationStage.SUBMITTED
            application.save(update_fields=["status", "stage", "submitted_at", "modified_at"])
            sync_lead_status(application, ApplicationStatus.RH_APPROVAL_PENDING)
            return HttpResponse.Success({
                "message": "Selfie submitted. Application moved to RH Approval Pending.",
                "status": application.status
            })

        try:
            from onboarding_v2 import views as views_module

            views_module.enqueue_pre_screen(application)
            logger.info(
                "Submit pre-screen | app=%s req_id=%s",
                application.application_id,
                application.saas_request_id,
            )

            response_payload = {
                "application": ApplicationV2Serializer(application).data,
                "message": "Submission accepted; pre-screen task enqueued.",
            }
            logger.info("Submit pre-screen response | app=%s response=%s", application_id, response_payload)
            return HttpResponse.Success(response_payload)
        except ValueError as ve:
            return HttpResponse.BadRequest(str(ve))
        except Exception as exc:
            logger.exception("Submit pre-screen failed | app=%s payload=%s", application_id, request.data)
            from onboarding_v2 import views as views_module

            views_module.notify_app_step_error(
                application_id, "SUBMIT_PRE_SCREEN", str(exc), payload=request.data
            )
            return HttpErrors.InternalServerError("Failed to submit pre-screen")


class CorrectionRaiseView(APIView):
    """
    GET  /applications/<application_id>/correction/  – List all corrections for an application.
         Optional query param: ?status=PENDING|RESOLVED
    POST /applications/<application_id>/correction/  – Raise one or many corrections.
         Updates application status to CORRECTION_RAISED_BY_UNDERWRITING.
    """

    authentication_classes = [SaasWebhookAuthentication, OAuth2Authentication]

    @extend_schema(
        tags=["Onboarding V2 - Corrections"],
        operation_id="correction_list",
        summary="List all corrections for an application",
        description=(
            "Fetches all correction records raised for the given application. "
            "Returns corrections ordered by most recent first. "
            "Optionally filter by status using the `status` query parameter."
        ),
        parameters=[
            OpenApiParameter(
                name="application_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Unique application identifier (e.g. MPAGL0183).",
                required=True,
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter corrections by status. Allowed values: `PENDING`, `RESOLVED`.",
                required=False,
                enum=["PENDING", "RESOLVED"],
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="CorrectionListResponse",
                    fields={
                        "status": drf_serializers.CharField(default="success"),
                        "data": inline_serializer(
                            name="CorrectionListData",
                            fields={
                                "application_id": drf_serializers.CharField(),
                                "count": drf_serializers.IntegerField(),
                                "corrections": CorrectionOnboardingListSerializer(many=True),
                            },
                        ),
                    },
                ),
                description="Corrections fetched successfully.",
            ),
            400: OpenApiResponse(description="Application not found."),
            500: OpenApiResponse(description="Internal server error."),
        },
        examples=[
            OpenApiExample(
                name="All Corrections Response",
                response_only=True,
                value={
                    "status": "success",
                    "data": {
                        "application_id": "MPAGL0183",
                        "count": 2,
                        "corrections": [
                            {
                                "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                                "application_id": "MPAGL0183",
                                "stage": "PAN",
                                "field_name": "pan_number",
                                "image_id": None,
                                "payload": {},
                                "status": "PENDING",
                                "created_at": "2024-03-25T10:00:00Z",
                                "modified_at": "2024-03-25T10:00:00Z",
                            },
                            {
                                "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                                "application_id": "MPAGL0183",
                                "stage": "ADDRESS",
                                "field_name": "pincode",
                                "image_id": None,
                                "payload": {"expected": "560001"},
                                "status": "RESOLVED",
                                "created_at": "2024-03-24T09:00:00Z",
                                "modified_at": "2024-03-24T09:30:00Z",
                            },
                        ],
                    },
                },
            ),
        ],
    )
    def get(self, request, application_id):
        try:
            try:
                application = ApplicationV2.objects.get(application_id=application_id)
            except ApplicationV2.DoesNotExist:
                return HttpResponse.BadRequest("Application not found")

            qs = CorrectionOnboarding.objects.filter(application=application).order_by("-created_at")

            status_filter = request.query_params.get("status")
            if status_filter:
                qs = qs.filter(status=status_filter.upper())
            else:
                qs = qs.filter(status=CorrectionOnboarding.Status.PENDING)

            serializer = CorrectionOnboardingListSerializer(qs, many=True)
            return HttpResponse.Success(
                {
                    "application_id": application_id,
                    "count": qs.count(),
                    "corrections": serializer.data,
                }
            )
        except Exception as exc:
            logger.exception("Fetching corrections failed | app=%s", application_id)
            return HttpErrors.InternalServerError("Fetching corrections failed")

    @extend_schema(
        tags=["Onboarding V2 - Corrections"],
        operation_id="correction_raise",
        summary="Raise corrections for an application",
        description=(
            "Raises one or multiple correction entries for a specific application. "
            "Accepts either a single correction object or a list of correction objects. "
            "On success, the application status is automatically updated to "
            "`CORRECTION_RAISED_BY_UNDERWRITING`."
        ),
        parameters=[
            OpenApiParameter(
                name="application_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="Unique application identifier (e.g. MPAGL0183).",
                required=True,
            ),
        ],
        request=inline_serializer(
            name="CorrectionRaiseRequest",
            fields={
                "stage": drf_serializers.ChoiceField(
                    choices=[s[0] for s in ApplicationStage.choices],
                    help_text="The application stage where the correction is needed (e.g. PAN, ADDRESS).",
                ),
                "field_name": drf_serializers.CharField(
                    max_length=255,
                    help_text="The specific field that needs correction (e.g. pan_number).",
                ),
                "image_id": drf_serializers.CharField(
                    required=False,
                    allow_null=True,
                    help_text="Optional reference image ID associated with the correction.",
                ),
                "payload": drf_serializers.JSONField(
                    required=False,
                    help_text="Optional extra data for the correction (e.g. expected values).",
                ),
            },
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="CorrectionRaiseResponse",
                    fields={
                        "status": drf_serializers.CharField(default="success"),
                        "data": inline_serializer(
                            name="CorrectionRaiseData",
                            fields={
                                "message": drf_serializers.CharField(),
                                "application_id": drf_serializers.CharField(),
                                "status": drf_serializers.CharField(),
                            },
                        ),
                    },
                ),
                description="Correction(s) raised successfully.",
            ),
            400: OpenApiResponse(description="Validation error or application not found."),
            500: OpenApiResponse(description="Internal server error."),
        },
        examples=[
            OpenApiExample(
                name="Single Correction",
                request_only=True,
                value={
                    "stage": "PAN",
                    "field_name": "pan_number",
                    "image_id": None,
                    "payload": {},
                },
            ),
            OpenApiExample(
                name="Multiple Corrections (List)",
                request_only=True,
                value=[
                    {
                        "stage": "PAN",
                        "field_name": "pan_number",
                        "image_id": None,
                        "payload": {},
                    },
                    {
                        "stage": "ADDRESS",
                        "field_name": "pincode",
                        "image_id": "img_abc123",
                        "payload": {"expected": "560001"},
                    },
                ],
            ),
            OpenApiExample(
                name="Success Response",
                response_only=True,
                value={
                    "status": "success",
                    "data": {
                        "message": "2 correction(s) raised successfully",
                        "application_id": "MPAGL0183",
                        "status": "CORRECTION_RAISED_BY_UNDERWRITING",
                    },
                },
            ),
        ],
    )
    def post(self, request, application_id):
        try:
            try:
                application = ApplicationV2.objects.get(application_id=application_id)
            except ApplicationV2.DoesNotExist:
                return HttpResponse.BadRequest("Application not found")

            is_many = isinstance(request.data, list)
            serializer = CorrectionRaiseSerializer(data=request.data, many=is_many)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            corrections_data = (
                serializer.validated_data if is_many else [serializer.validated_data]
            )

            # Check if any CHEQUE_PRIMARY field is present, and add all others if needed
            cheque_primary_fields = [
                "documents.cheque_primary.metadata.IFSC_code",
                "documents.cheque_primary.metadata.full_name",
                "documents.cheque_primary.metadata.account_number",
                "documents.cheque_primary.metadata.bank_name",
            ]
            existing_fields = {d["field_name"] for d in corrections_data}
            has_cheque_primary = any(field in existing_fields for field in cheque_primary_fields)
            
            if has_cheque_primary:
                # Find the first CHEQUE_PRIMARY entry (any of the fields)
                sample_data = next(d for d in corrections_data if d["field_name"] in cheque_primary_fields)
                for field in cheque_primary_fields:
                    if field not in existing_fields:
                        corrections_data.append({
                            "stage": sample_data["stage"],
                            "field_name": field,
                            "image_id": sample_data.get("image_id"),
                            "payload": sample_data.get("payload") or {}
                        })
                        existing_fields.add(field)

            # Create correction records
            for data in corrections_data:
                stage = data["stage"]
                field_name = data["field_name"]
                image_id = data.get("image_id")
                payload = data.get("payload") or {}

                CorrectionOnboarding.objects.create(
                    application=application,
                    stage=stage,
                    field_name=field_name,
                    image_id=image_id,
                    payload=payload,
                    status=CorrectionOnboarding.Status.PENDING,
                )

            # Update application status
            application.status = ApplicationStatus.CORRECTION_RAISED_BY_UNDERWRITING
            application.save(update_fields=["status", "modified_at"])

            return HttpResponse.Success(
                {
                    "message": f"{len(corrections_data)} correction(s) raised successfully",
                    "application_id": application_id,
                    "status": application.status,
                }
            )
        except Exception as exc:
            logger.exception("Raising correction failed | app=%s", application_id)
            return HttpErrors.InternalServerError("Raising correction failed")


class RHActionView(APIView):
    """
    Handle RH actions: APPROVE, REJECT, CORRECTION.
    """

    @extend_schema(
        tags=["Onboarding V2 - RH Actions"],
        operation_id="rh_action",
        summary="Handle RH actions (Approve/Reject/Correction)",
        request=RHActionSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="RHActionResponse",
                    fields={
                        "status": drf_serializers.CharField(default="success"),
                        "data": inline_serializer(
                            name="RHActionData",
                            fields={
                                "message": drf_serializers.CharField(),
                                "application_id": drf_serializers.CharField(),
                                "status": drf_serializers.CharField(),
                            },
                        ),
                    },
                ),
                description="RH action processed successfully.",
            ),
            400: OpenApiResponse(description="Invalid request or application state."),
            500: OpenApiResponse(description="Internal server error."),
        },
    )
    def post(self, request, application_id):
        try:
            try:
                application = ApplicationV2.objects.get(application_id=application_id)
            except ApplicationV2.DoesNotExist:
                return HttpResponse.BadRequest("Application not found")

            serializer = RHActionSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            if getattr(request.user, "is_authenticated", False):
                application._status_changed_by = request.user

            action = serializer.validated_data["status"]
            remarks = serializer.validated_data.get("remarks")
            reason = serializer.validated_data.get("reason")

            application.rh_remarks = remarks
            application.rh_rejection_reason = reason

            if action == "APPROVE":
                application.status = ApplicationStatus.APPROVED_BY_RH
                from onboarding_v2.helpers import saas_helpers
                saas_helpers.enqueue_rh_approval_notification(application)
            elif action == "REJECT":
                application.status = ApplicationStatus.REJECTED_BY_RH
            elif action == "CORRECTION":
                application.status = ApplicationStatus.CORRECTION_RAISED_BY_RH
                # Create correction record for Selfie stage as per user requirement
                CorrectionOnboarding.objects.create(
                    application=application,
                    stage=ApplicationStage.SELFIE,
                    field_name="image",
                    image_id="1",
                    payload={"reason": reason, "remarks": remarks},
                    status=CorrectionOnboarding.Status.PENDING,
                )

            application.save(
                update_fields=["status", "rh_remarks", "rh_rejection_reason", "modified_at"]
            )
            sync_lead_status(application, application.status)

            return HttpResponse.Success(
                {
                    "message": f"RH {action} successful",
                    "application_id": application_id,
                    "status": application.status,
                }
            )
        except Exception as exc:
            logger.exception("RH action failed | app=%s", application_id)
            return HttpErrors.InternalServerError("RH action failed")


class ApplicationStateView(APIView):
    """
    Returns application status, stages, progress, and saved snapshots for resume/prefill.
    """

    def get(self, request, application_id):
        logger.info("Application state request | app=%s payload=%s", application_id, request.query_params)
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")
        
        stages = request.query_params.get("stages")
        context = {}
        if stages:
            context["filter_stages"] = [s.strip().upper() for s in stages.split(",") if s.strip()]
            
        data = ApplicationStateSerializer(application, context=context).data
        response_payload = {"application": data}
        logger.info("Application state response | app=%s response=%s", application_id, response_payload)
        return HttpResponse.Success(response_payload)

    @extend_schema(
        tags=["Onboarding V2"],
        summary="Partially update an application",
        request=ApplicationV2Serializer,
        responses={200: ApplicationV2Serializer, 400: OpenApiTypes.STR, 404: OpenApiTypes.STR}
    )
    def patch(self, request, application_id):
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
            serializer = ApplicationV2Serializer(application, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success(serializer.data)
            return HttpResponse.BadRequest(serializer.errors)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.NotFound("Application not found")
        except Exception as e:
            return HttpErrors.InternalServerError(str(e))

    @extend_schema(
        tags=["Onboarding V2"],
        summary="Delete an application",
        responses={200: OpenApiTypes.STR, 404: OpenApiTypes.STR}
    )
    def delete(self, request, application_id):
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
            application.delete()
            return HttpResponse.Success("Application deleted successfully")
        except ApplicationV2.DoesNotExist:
            return HttpResponse.NotFound("Application not found")
        except Exception as e:
            return HttpErrors.InternalServerError(str(e))


class FinalizeApplicationView(APIView):
    """
    Trigger create-loan and doc upload to SAAS for post-screened applications.
    """

    def post(self, request, application_id):
        logger.info("Finalize application request | app=%s payload=%s", application_id, request.data)
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        # Skip SAAS creation for fresh loans
        if application.loan_type == LeadType.FRESH:
            application.status = ApplicationStatus.PUNCHING_PENDING
            application.save()
            sync_lead_status(application, ApplicationStatus.PUNCHING_PENDING)
            return HttpResponse.Success({
                "application_id": application.application_id,
                "message": "Application status updated to Punching Pending for fresh loan.",
            })

        try:
            from onboarding_v2 import views as views_module

            views_module.enqueue_create_loan(application)

            response_payload = {
                "application_id": application.application_id,
                "message": "Create-loan enqueued. Document URLs can be shared via presigned GET.",
            }
            logger.info("Finalize application response | app=%s response=%s", application_id, response_payload)
            return HttpResponse.Success(response_payload)
        except ValueError as ve:
            return HttpResponse.BadRequest(str(ve))
        except Exception as exc:
            logger.exception("Finalize application failed | app=%s", application_id)
            from onboarding_v2 import views as views_module

            views_module.notify_app_step_error(application_id, "FINALIZE", str(exc), payload=request.data)
            return HttpErrors.InternalServerError("Failed to finalize application")


class FundRefundStatementView(APIView):
    """
    Returns the summary and transaction statement for Fund Refunds.
    """

    def get(self, request, application_id):
        try:
            try:
                application = ApplicationV2.objects.get(application_id=application_id)
            except ApplicationV2.DoesNotExist:
                return HttpResponse.BadRequest("Application not found")

            lead = application.lead
            current_payload = application.stage_payload if isinstance(application.stage_payload, dict) else {}
            refunds = current_payload.get("fund_refund", [])
            if not isinstance(refunds, list):
                refunds = []
            
            # If no refunds in stage_payload, check the stage snapshot
            if not refunds:
                try:
                    snapshot = application.stage_snapshots.get(stage=ApplicationStage.FUND_REFUND)
                    if isinstance(snapshot.payload, list):
                        refunds = snapshot.payload
                except Exception:
                    pass

            refund_amounts = calculate_fund_refund_amounts(application)
            statement = []

            for r in refunds:
                amt = Decimal(str(r.get("amount", "0")))
                
                # Get cheque_image_urls
                cheque_image_urls = r.get("cheque_image_urls") or []
                if not cheque_image_urls and r.get("cheque_image_url"):
                    if isinstance(r.get("cheque_image_url"), list):
                        cheque_image_urls = r.get("cheque_image_url")
                    else:
                        cheque_image_urls = [r.get("cheque_image_url")]
                
                # Derive cheque_image_url for backwards compatibility
                cheque_image_url = r.get("cheque_image_url")
                if not cheque_image_url and cheque_image_urls:
                    cheque_image_url = cheque_image_urls[0]
                
                statement.append({
                        "id": r.get("id"),
                        "amount": str(amt),
                        "payment_mode": r.get("payment_mode"),
                        "transaction_reference_number": r.get("transaction_reference_number"),
                        "status": r.get("status"),
                        "created_at": r.get("created_at"),
                        "bank_name": r.get("bank_name"),
                        "cheque_image_urls": cheque_image_urls,
                        "cheque_image_url": cheque_image_url,
                        "transaction_proof_url": r.get("transaction_proof_url"),
                        "relationship": r.get("relationship"),
                        "relationship_proof_url": r.get("relationship_proof_url"),
                    })

            # Sort statement by date (newest first)
            statement.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            response_data = {
                "loan_request_id": application.application_id,
                "customer_name": lead.customer_name,
                "mobile_number": lead.contact_number,
                "sanctioned_amount": str(refund_amounts["sanctioned_amount"]),
                "deposited_amount": str(refund_amounts["deposited_amount"]),
                "pending_amount": str(refund_amounts["pending_amount"]),
                "not_verified_amount": str(refund_amounts["not_verified_amount"]),
                "statement": statement
            }

            return HttpResponse.Success(response_data)
        except Exception as exc:
            logger.exception("Fetching fund refund statement failed | app=%s", application_id)
            return HttpErrors.InternalServerError("Fetching statement failed")


class CustomerDefaulterCheckView(APIView):
    """
    Check whether a PAN/contact number belongs to a defaulter in Customers.
    """
    permission_classes = []

    def post(self, request):
        serializer = CustomerDefaulterCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return HttpResponse.BadRequest(serializer.errors)

        pan_number = serializer.validated_data["pan_number"]
        contact_number = serializer.validated_data["contact_number"]
        customer_query = _build_customer_defaulter_query(pan_number, contact_number)

        matched_customer = (
            Customers.objects.filter(customer_query)
            .order_by("-is_defaulter", "-modified_at")
            .first()
        )

        is_defaulter = bool(matched_customer and matched_customer.is_defaulter)
        return HttpResponse.Success({
            "is_defaulter": is_defaulter,
            "customer_found": bool(matched_customer),
            "message": (
                "This applicant cannot be onboarded due to adverse repayment history."
                if is_defaulter
                else "not_defaulter"
            ),
        })


class ValidatePanView(APIView):
    """
    Validate PAN and Phone number combination before stage submission.
    Checks for:
    1. Phone being linked to another customer (Scenario 4)
    2. Identity mismatch (Scenario 5)
    """
    permission_classes = []

    def post(self, request):
        pan_number = request.data.get("pan_card_number")
        phone = request.data.get("contact_number")

        if not pan_number or not phone:
            return HttpResponse.Success({
                "message": "pan_card_number and contact_number are required.",
                "valid": False
            })

        # Check if the user is a defaulter in the Customers table
        from onboarding_v2.models import Customers
        from django.db.models import Q

        clean_pan = pan_number.strip().upper() if pan_number else ""
        clean_phone_digits = "".join(ch for ch in phone if ch.isdigit()) if phone else ""

        customer_query = Q()
        if clean_pan:
            customer_query |= Q(pan_number__iexact=clean_pan)
        if len(clean_phone_digits) >= 10:
            last_10_phone = clean_phone_digits[-10:]
            customer_query |= Q(phone_number__endswith=last_10_phone)

        if customer_query:
            defaulter_exists = Customers.objects.filter(customer_query, is_defaulter=True).exists()
            if defaulter_exists:
                return HttpResponse.Success({
                    "message": "defaulter",
                    "valid": False
                })

        # 1. Find PAN Owner
        pan_owner_lead = None
        from onboarding_v2.models import ApplicationDocument, LeadV2, ApplicationV2
        from onboarding_v2.constants import DocumentType

        pan_doc = (
            ApplicationDocument.objects.filter(
                document_type=DocumentType.PAN,
                metadata__pan_number=pan_number
            )
            .select_related("application__lead")
            .first()
        )

        if pan_doc and pan_doc.application and pan_doc.application.lead:
            pan_owner_lead = pan_doc.application.lead
        else:
            # Fallbacks: try to resolve PAN owner from snapshots or application payloads
            try:
                from onboarding_v2.models import ApplicationStageSnapshot as Snap
                snap = (
                    Snap.objects.filter(
                        stage=ApplicationStage.PAN,
                        payload__pan_number=pan_number,
                    )
                    .select_related("application__lead")
                    .order_by("-modified_at")
                    .first()
                )
                if snap and getattr(snap, "application", None) and getattr(snap.application, "lead", None):
                    pan_owner_lead = snap.application.lead
            except Exception:
                pass
            if not pan_owner_lead:
                app_with_pan = (
                    ApplicationV2.objects.filter(
                        stage_payload__pan_number=pan_number
                    )
                    .select_related("lead")
                    .first()
                )
                if app_with_pan and getattr(app_with_pan, "lead", None):
                    pan_owner_lead = app_with_pan.lead

        # 2. Find Phone Owner
        phone_owner_lead = (
            LeadV2.objects.filter(contact_number=phone, customer_id__isnull=False)
            .exclude(customer_id="")
            .first()
        )

        if not phone_owner_lead:
            other_app = (
                ApplicationV2.objects.filter(
                    stage_payload__contact_number=phone
                )
                .select_related("lead")
                .first()
            )
            if other_app and other_app.lead:
                phone_owner_lead = other_app.lead

        def _mask_phone(num: str) -> str:
            if not num:
                return ""
            return "+" + ("X" * max(len(num) - 4, 0)) + num[-4:]

        def _mask_pan(p: str) -> str:
            if not p:
                return ""
            last4 = "".join(ch for ch in p if ch.isdigit())[-4:]
            return "XXXXXX" + last4 if last4 else "XXXXXX"

        # Case 1: Both duplicate and linked together
        if pan_owner_lead and phone_owner_lead and pan_owner_lead.customer_id == phone_owner_lead.customer_id:
            msg = f"We already have the details of Customer: {pan_owner_lead.customer_name} ({pan_owner_lead.customer_id})"
            return HttpResponse.Success({"message": msg, "valid": True})

        # Case 2: PAN exists, phone new
        if pan_owner_lead and not phone_owner_lead:
            linked_phone = getattr(pan_owner_lead, "contact_number", "") or ""
            masked_phone = _mask_phone(linked_phone)
            msg = f"PAN already exist with {masked_phone}, Continue with new phone number?"
            return HttpResponse.Success({"message": msg, "valid": True})

        # Case 3: Phone exists, PAN new
        if not pan_owner_lead and phone_owner_lead:
            return HttpResponse.Success({
                "message": "Entered phone number is already linked with different pan. Please create a new lead with new phone number",
                "valid": False
            })

        # Case 4: Both exist but linked to different customers
        if pan_owner_lead and phone_owner_lead and pan_owner_lead.customer_id != phone_owner_lead.customer_id:
            # Show the phone number associated with the PAN owner (correct linkage)
            linked_phone = getattr(pan_owner_lead, "contact_number", "") or ""
            masked_phone = _mask_phone(linked_phone)
            return HttpResponse.Success({
                "message": f"Entered phone number is already linked with different pan. Please create a new lead with new phone number or use linked phone number '{masked_phone}'",
                "valid": False
            })

        msg = "Valid."
        return HttpResponse.Success({"message": msg, "valid": True})


class AadhaarVerifyView(APIView):
    """
    Verify Aadhaar number against PAN using Zoop API.
    Retrieves PAN details from the application's PAN stage and verifies
    if the provided Aadhaar number matches the masked Aadhaar returned by Zoop.
    """
    authentication_classes = [OAuth2Authentication, SaasWebhookAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = []

    def post(self, request, application_id):
        aadhaar_number = request.data.get("aadhaar_number")
        if not aadhaar_number:
            return HttpResponse.BadRequest("aadhaar_number is required")

        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        # 1. Get PAN details from PAN stage snapshot or lead
        pan_number = None
        pan_holder_name = None

        try:
            snapshot = application.stage_snapshots.get(stage=ApplicationStage.PAN)
            payload = snapshot.payload
            if isinstance(payload, dict):
                pan_number = payload.get("pan_number")
                pan_holder_name = payload.get("name_on_pan")
        except ApplicationStageSnapshot.DoesNotExist:
            pass

        if not pan_number:
            pan_number = application.lead.pan_number
            pan_holder_name = application.lead.customer_name

        if not pan_number:
            return HttpResponse.BadRequest("PAN details not found for this application")

        # 2. Call Zoop PAN verification API
        task_id = str(uuid.uuid4())
        payload = {
            "mode": "sync",
            "data": {
                "customer_pan_number": pan_number,
                "pan_holder_name": pan_holder_name or application.lead.customer_name,
                "consent": "Y",
                "consent_text": "I hereby give my consent to verify my PAN details via Zoop API."
            },
            "task_id": task_id
        }

        headers = {
            "app-id": settings.ZOOP_APP_ID,
            "api-key": settings.ZOOP_API_KEY,
            "Content-Type": "application/json"
        }

        try:
            logger.info("Calling Zoop PAN verification for application %s", application_id)
            response = requests.post(settings.ZOOP_PAN_URL, json=payload, headers=headers)
            zoop_data = response.json()
            logger.info("Zoop PAN verification response for application %s: %s", application_id, zoop_data)
            if zoop_data.get("response_code") != "100" or not zoop_data.get("success"):
                error_msg = zoop_data.get("response_message") or zoop_data.get("message") or "Unknown error"
                return HttpResponse.BadRequest(f"Zoop API error: {error_msg}")

            result = zoop_data.get("result", {})
            masked_aadhaar = result.get("masked_aadhaar")

            if masked_aadhaar is None:
                return HttpResponse.BadRequest("Masked Aadhaar not returned by Zoop")

            # 3. Verify Aadhaar
            # Handles patterns like 'XXXXXXXX6806' or '12XXXXXX34'
            is_match = False
            clean_aadhaar = str(aadhaar_number).strip()
            clean_masked = str(masked_aadhaar).strip().upper()

            if len(clean_aadhaar) != 12:
                return HttpResponse.BadRequest("Invalid Aadhaar number length. Expected 12 digits.")

            if clean_masked == "":
                is_match = True
            else:
                # Create a regex pattern by replacing 'X' with '.'
                pattern = clean_masked.replace('X', '.')
                if re.fullmatch(pattern, clean_aadhaar):
                    is_match = True
            
            if is_match:
                return HttpResponse.Success({
                    "message": "Aadhaar verification successful",
                    "masked_aadhaar": masked_aadhaar,
                    "match": True
                })
            else:
                return HttpResponse.BadRequest({
                    "message": "Aadhaar number does not match with the PAN linked Aadhaar",
                    "masked_aadhaar": masked_aadhaar,
                    "match": False
                })

        except Exception as e:
            logger.exception("Aadhaar verification failed for application %s", application_id)
            return HttpResponse.InternalServerError(str(e))


class BankVerifyView(APIView):
    """
    Verify Bank Account details using Zoop API.
    Retrieves bank details from the request and calls Zoop's Bank Account Verification (Advance) API.
    """
    authentication_classes = [OAuth2Authentication, SaasWebhookAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = []

    def post(self, request, application_id):
        account_number = request.data.get("account_number")
        ifsc = request.data.get("ifsc")
        name_to_match = request.data.get("name_to_match")

        if not account_number or not ifsc:
            return HttpResponse.BadRequest("account_number and ifsc are required")

        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        # If name_to_match is not provided, use the customer name from lead
        if not name_to_match:
            name_to_match = application.lead.customer_name

        task_id = str(uuid.uuid4())
        
        # Hybrid consent handling
        consent_text = request.data.get(
            "consent_text",
            "I hereby give my consent to verify my bank account details via Zoop API."
        )

        payload = {
            "mode": "sync",
            "data": {
                "account_number": account_number,
                "ifsc": ifsc,
                "consent": "Y",
                "name_to_match": name_to_match,
                "consent_text": consent_text
            },
            "task_id": task_id
        }

        headers = {
            "app-id": settings.ZOOP_APP_ID,
            "api-key": settings.ZOOP_API_KEY,
            "Content-Type": "application/json"
        }

        try:
            logger.info("Calling Zoop Bank verification for application %s", application_id)
            response = requests.post(settings.ZOOP_BANK_VERIFICATION_LITE_URL, json=payload, headers=headers)
            zoop_data = response.json()
            
            # Use the same response handler logic as the original zoop app if possible
            # But since we are in onboarding_v2, we'll return a consistent HttpResponse
            
            if zoop_data.get("response_code") != "100" or not zoop_data.get("success"):
                error_msg = zoop_data.get("response_message") or zoop_data.get("message") or "Unknown error"
                return HttpResponse.BadRequest({
                    "message": f"Zoop API error: {error_msg}",
                    "zoop_response": zoop_data
                })

            # Save the verification result to the application's BANK stage if needed
            # For now, we just return the success response with data
            
            return HttpResponse.Success({
                "message": "Bank account verification successful",
                "data": zoop_data
            })

        except Exception as e:
            logger.exception("Bank verification failed for application %s", application_id)
            return HttpResponse.InternalServerError(str(e))
