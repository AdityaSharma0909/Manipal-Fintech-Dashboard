import json
import logging
import json
import math
import re
import re
import traceback
import uuid

from django.conf import settings
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from django.db.models import Q
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
) 

from lead.models import NewLead
from lead.serializers import NewLeadSerializer
# from masters.models import PincodeMaster
from utils.responseHandler import HttpResponse
from utility.error_handler import HttpErrors
from onboarding_v2.models import (
    ApplicationV2,
    BankLeadTrace,
    LeadAutoClosureSetting,
    LeadV2,
    ApplicationDocument,
    WebhookEvent,
)
from onboarding_v2.serializers import (
    ApplicationListSerializer,
    ApplicationCreateSerializer,
    ApplicationV2Serializer,
    LeadAutoClosureSettingSerializer,
    LeadCreateSerializer,
)
from onboarding_v2.helpers.lead_application_helpers import (
    create_lead,
    filter_applications,
    filter_leads,
    prepare_application_create_data,
    prepare_lead_create_data,
)
from onboarding_v2.integrations.axis.service import sendToAxis
from onboarding_v2.integrations.bank_trace import json_safe, mask_headers, update_bank_lead_trace
from onboarding_v2.integrations.icici.service import sendToIcici
from onboarding_v2.integrations.bajaj.service import sendToBajaj, extract_bajaj_lead_id
from onboarding_v2.views.common import DefaultPagination
from users.models import User
from utils.constants import ROLES
from crif_bureau.models import CrifBureauReportTrace, CrifBureauTrace
from onboarding_v2.constants import (
    ApplicationStatus,
    LeadStatus,
    ApplicationStage,
    LeadType,
    DocumentType,
)
from users.serializers import UserResponseSerializer


logger = logging.getLogger(__name__)


def _normalize_phone_for_crif(value):
    digits = re.sub(r"\D", "", str(value or ""))
    return digits[-10:] if len(digits) >= 10 else digits


def _get_crif_eligible_score_threshold():
    raw_value = getattr(settings, "CRIF_BUREAU_ELIGIBLE_SCORE", None)
    if raw_value in (None, ""):
        return None
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        logger.warning("Invalid CRIF_BUREAU_ELIGIBLE_SCORE configured | value=%r", raw_value)
        return None


def _resolve_crif_lead_eligibility(contact_number):
    threshold = _get_crif_eligible_score_threshold()
    if threshold is None:
        return None

    phone = _normalize_phone_for_crif(contact_number)
    if not phone:
        return None

    # ``bureau_report/`` stores synchronous report results in
    # CrifBureauReportTrace. Keep the older trace as a fallback for the
    # consent/webhook-based CRIF flow.
    trace = CrifBureauReportTrace.objects.filter(phone_number=phone).first()
    if not trace or trace.score is None:
        trace = CrifBureauTrace.objects.filter(phone_number=phone).first()
    if not trace or trace.score is None:
        return None

    is_eligible = int(trace.score) >= threshold
    return {
        "eligible": is_eligible,
        "score": int(trace.score),
        "threshold": threshold,
        "phone_number": phone,
        "trace_id": trace.id,
    }


def _format_axis_duplicate_message(message):
    if not message:
        return None

    match = re.search(
        r"Lead\s+id\s+([A-Za-z0-9_-]+)\s+with\s+the\s+same\s+Mobile\s+number\s+(\d+).*already\s+exists",
        str(message),
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None

    lead_id, mobile_number = match.groups()
    return f"There is already an existing Lead No: {lead_id} for mobile no :{mobile_number}."


def _axis_error_message(exc):
    message = getattr(exc, "partner_message", None)
    if message:
        message = str(message)
        return _format_axis_duplicate_message(message) or message

    message = str(exc)
    return _format_axis_duplicate_message(message) or message


def _is_axis_duplicate_error(message):
    return bool(message and message.startswith("There is already an existing Lead No:"))


def _extract_icici_lead_id(response):
    if not isinstance(response, dict):
        return None

    direct_lead_id = (
        response.get("LeadNumber")
        or response.get("leadNumber")
        or response.get("leadId")
        or response.get("LeadID")
    )
    if direct_lead_id:
        return direct_lead_id

    nested_response = response.get("Response")
    if isinstance(nested_response, str):
        try:
            nested_response = json.loads(nested_response)
        except json.JSONDecodeError:
            pass

    if isinstance(nested_response, dict):
        nested_lead_id = (
            nested_response.get("LeadNumber")
            or nested_response.get("leadNumber")
            or nested_response.get("leadId")
            or nested_response.get("LeadID")
        )
        if nested_lead_id:
            return nested_lead_id
        nested_response = nested_response.get("Response")

    if isinstance(nested_response, str):
        match = re.search(r"\bLead\s*Number\s*(?:is|:)?\s*([A-Za-z0-9_-]+)", nested_response, re.IGNORECASE)
        if match:
            return match.group(1)

    return None


def _decode_icici_nested_response(response):
    nested_response = response
    for _ in range(3):
        if isinstance(nested_response, dict) and "Response" in nested_response:
            nested_response = nested_response.get("Response")
        elif isinstance(nested_response, str):
            try:
                nested_response = json.loads(nested_response)
            except json.JSONDecodeError:
                break
        else:
            break
    return nested_response


def _icici_duplicate_error_message(response):
    if not isinstance(response, dict):
        return None

    nested_response = _decode_icici_nested_response(response)
    text_parts = []

    def collect_text(value):
        if isinstance(value, dict):
            for item in value.values():
                collect_text(item)
        elif isinstance(value, list):
            for item in value:
                collect_text(item)
        elif value is not None:
            text_parts.append(str(value))

    collect_text(nested_response)
    if nested_response is not response:
        for key in ("StatusText", "statusText", "message", "Message"):
            if response.get(key):
                text_parts.append(str(response.get(key)))

    message = " ".join(text_parts).strip()
    normalized = message.lower()
    duplicate_markers = (
        "duplicate",
        "already exists",
        "cannot be created",
        "new lead cannot be created",
        "A lead already exists with same details.",
        "New Lead Cannot be created.",
        "A lead already exists with same details."
    )
    if any(marker in normalized for marker in duplicate_markers):
        return message or "A lead already exists with same details."
    return None


def _safe_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _create_bank_lead_trace(request, payload):
    try:
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        return BankLeadTrace.objects.create(
            created_by=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
            bank_name=payload.get("bank"),
            contact_number=payload.get("contact_number"),
            lead_type=payload.get("lead_type"),
            crm_type=payload.get("crm_type") or metadata.get("crm_type"),
            metadata={
                "onboarding_request_headers": mask_headers(dict(request.headers.items())),
                "onboarding_request_payload": json_safe(payload),
            },
        )
    except Exception:
        logger.exception("Failed to create BankLeadTrace")
        return None


def _update_bank_lead_trace(trace, **fields):
    update_bank_lead_trace(trace, **fields)


class LeadCreateView(APIView):
    @extend_schema(
        tags=["Onboarding V2"],
        summary="Create a new lead",
        description="Creates a new lead in the Onboarding V2 system.",
        request=LeadCreateSerializer,
        examples=[
            OpenApiExample(
                name="Gold Loan Balance Transfer Lead Payload",
                value={
                    "contact_number": "7001586476",
                    "customer_name": "Tamoghna Mondal",
                    "product_category": "LOAN",
                    "product_subcategory": "GOLD_LOAN",
                    "lead_type": "BALANCE_TRANSFER",
                    "amount": "150000",
                    "pincode": "560001",
                    "source": "SELF",
                },
                request_only=True,
            ),
        ],
        responses={
            200: LeadCreateSerializer,
            400: OpenApiTypes.STR,
            500: OpenApiTypes.STR,
        },
    )
    def post(self, request):
        logger.info("Create Lead Request| payload=%s", request.data)
        if request.user.role == ROLES.REGIONAL_HEAD.value:
            return HttpResponse.BadRequest("RH users are not allowed to create leads.")
        bank_trace = None
        try:
            payload = prepare_lead_create_data(request.user, request.data)
            bureau_eligibility = _resolve_crif_lead_eligibility(payload.get("contact_number"))
            if bureau_eligibility and not bureau_eligibility["eligible"]:
                payload["status"] = LeadStatus.NOT_ELIGIBLE
                lead = create_lead(payload)
                logger.info(
                    "Lead marked not eligible from CRIF trace | lead=%s phone=%s score=%s threshold=%s trace_id=%s",
                    lead.id,
                    bureau_eligibility["phone_number"],
                    bureau_eligibility["score"],
                    bureau_eligibility["threshold"],
                    bureau_eligibility["trace_id"],
                )
                return HttpResponse.Success({
                    "lead": LeadCreateSerializer(lead).data,
                    "bureau_eligibility": bureau_eligibility,
                })
            if bureau_eligibility and bureau_eligibility["eligible"]:
                # A caller may submit UNVERIFIED while the bureau step is in
                # progress. A successful bureau result is authoritative.
                payload["status"] = LeadStatus.ACTIVE
            
            # BANK_LEAD logic: Call Axis/ICICI first, only save if successful (200)
            lead_type = payload.get("lead_type")
            if lead_type == LeadType.BANK_LEAD:
                bank_trace = _create_bank_lead_trace(request, payload)
                serializer = LeadCreateSerializer(data=payload)
                if not serializer.is_valid():
                    _update_bank_lead_trace(
                        bank_trace,
                        status=BankLeadTrace.Status.VALIDATION_FAILED,
                        response_payload=serializer.errors,
                        response_status_code=400,
                        error_message="Validation failed",
                    )
                    return HttpResponse.BadRequest(serializer.errors)
                
                # Create unsaved lead instance for integration
                lead_obj = LeadV2(id=uuid.uuid4(), **serializer.validated_data)
                if bank_trace and not bank_trace.crm_type:
                    _update_bank_lead_trace(
                        bank_trace,
                        crm_type=(lead_obj.metadata or {}).get("crm_type"),
                        request_payload=payload,
                    )
                
                bank_name = payload.get("bank", "").upper()
                
                if "AXIS BANK" in bank_name:
                    # Add doc path from env as required (using mTLS cert path as confirmed)
                    import os
                    axis_env = os.getenv("AXIS_ENV", "UAT").upper()
                    doc_path = os.getenv(f"AXIS_{axis_env}_MTLS_CERT_FILE")
                    if doc_path:
                        meta = lead_obj.metadata or {}
                        meta["axis_doc_path"] = doc_path
                        lead_obj.metadata = meta
                        payload["metadata"] = meta

                    try:
                        axis_resp = sendToAxis(lead_obj, bank_trace=bank_trace)
                        logger.info("Axis integration response| lead_id=%s resp=%s", str(lead_obj.id), axis_resp)
                        axis_lead_id = None
                        if isinstance(axis_resp, dict):
                            axis_lead_id = (
                                axis_resp.get("Data", {}).get("leadId")
                                or axis_resp.get("leadId")
                                or axis_resp.get("itemKey")
                            )
                            if axis_lead_id:
                                payload["BankLeadID"] = axis_lead_id
                        _update_bank_lead_trace(
                            bank_trace,
                            bank_lead_id=axis_lead_id,
                        )
                    except Exception as exc:
                        axis_error_message = _axis_error_message(exc)
                        is_axis_duplicate = _is_axis_duplicate_error(axis_error_message)
                        if is_axis_duplicate:
                            logger.warning("Axis integration rejected for BANK_LEAD: %s", axis_error_message)
                        else:
                            logger.exception("Axis integration failed for BANK_LEAD")
                        _update_bank_lead_trace(
                            bank_trace,
                            status=BankLeadTrace.Status.FAILED,
                            response_status_code=400,
                            error_message=axis_error_message,
                        )
                        if is_axis_duplicate:
                            return HttpResponse.BadRequest(axis_error_message)
                        return HttpResponse.BadRequest(f"Axis integration failed: {axis_error_message}")
                
                elif "ICICI BANK" in bank_name:
                    try:
                        icici_resp = sendToIcici(lead_obj, bank_trace=bank_trace)
                        logger.info("ICICI integration response| lead_id=%s resp=%s", str(lead_obj.id), icici_resp)
                        icici_duplicate_message = _icici_duplicate_error_message(icici_resp)
                        if icici_duplicate_message:
                            _update_bank_lead_trace(
                                bank_trace,
                                status=BankLeadTrace.Status.REJECTED,
                                response_status_code=(
                                    _safe_int(icici_resp.get("statusCode"), 400)
                                    if isinstance(icici_resp, dict)
                                    else 400
                                ),
                                error_message=icici_duplicate_message,
                            )
                            return HttpResponse.BadRequest(f"ICICI integration rejected: {icici_duplicate_message}")
                        icici_lead_id = _extract_icici_lead_id(icici_resp)
                        if icici_lead_id:
                            payload["BankLeadID"] = icici_lead_id
                        else:
                            message = "ICICI integration failed: BankLeadID was not returned."
                            logger.warning(
                                "ICICI integration rejected for BANK_LEAD because BankLeadID is missing| lead_id=%s resp=%s",
                                str(lead_obj.id),
                                icici_resp,
                            )
                            _update_bank_lead_trace(
                                bank_trace,
                                status=BankLeadTrace.Status.FAILED,
                                response_status_code=(
                                    _safe_int(icici_resp.get("statusCode"), 400)
                                    if isinstance(icici_resp, dict)
                                    else 400
                                ),
                                error_message=message,
                            )
                            return HttpResponse.BadRequest(message)
                        _update_bank_lead_trace(
                            bank_trace,
                            bank_lead_id=icici_lead_id,
                        )
                    except Exception as exc:
                        logger.exception("ICICI integration failed for BANK_LEAD")
                        _update_bank_lead_trace(
                            bank_trace,
                            status=BankLeadTrace.Status.FAILED,
                            response_status_code=400,
                            error_message=str(exc),
                        )
                        return HttpResponse.BadRequest(f"ICICI integration failed: {str(exc)}")
                elif "BAJAJ" in bank_name or "BAJAJ FINSERV" in bank_name:
                    try:
                        bajaj_resp = sendToBajaj(lead_obj, bank_trace=bank_trace)
                        logger.info("Bajaj integration response| lead_id=%s resp=%s", str(lead_obj.id), bajaj_resp)
                        if isinstance(bajaj_resp, dict):
                            if bajaj_resp.get("status") == "Fail" or str(bajaj_resp.get("statusCode")) != "200":
                                message = bajaj_resp.get("message") or "Invalid Request"
                                _update_bank_lead_trace(
                                    bank_trace,
                                    status=BankLeadTrace.Status.FAILED,
                                    response_status_code=_safe_int(bajaj_resp.get("statusCode"), 400),
                                    error_message=message,
                                )
                                return HttpResponse.BadRequest(f"Bajaj integration failed: {message}")
                            data = bajaj_resp.get("data")
                            if isinstance(data, dict) and data.get("status") == "REJECT":
                                remarks = data.get("remarks") or "Lead rejected by Bajaj"
                                bajaj_rejected_lead_id = str(data.get("lead_id") or "") or None
                                rejected_message = (
                                    f"{remarks}, existing lead_id: {bajaj_rejected_lead_id}"
                                    if bajaj_rejected_lead_id
                                    else remarks
                                )
                                _update_bank_lead_trace(
                                    bank_trace,
                                    status=BankLeadTrace.Status.REJECTED,
                                    response_status_code=_safe_int(bajaj_resp.get("statusCode"), 400),
                                    error_message=rejected_message,
                                )
                                return HttpResponse.BadRequest(f"Bajaj integration rejected: {rejected_message}")
                        bajaj_lead_id = extract_bajaj_lead_id(bajaj_resp)
                        if bajaj_lead_id:
                            payload["BankLeadID"] = bajaj_lead_id
                        _update_bank_lead_trace(
                            bank_trace,
                            response_status_code=_safe_int(bajaj_resp.get("statusCode"), 200) if isinstance(bajaj_resp, dict) else None,
                            bank_lead_id=bajaj_lead_id,
                        )
                    except Exception as exc:
                        logger.exception("Bajaj integration failed for BANK_LEAD")
                        _update_bank_lead_trace(
                            bank_trace,
                            status=BankLeadTrace.Status.FAILED,
                            response_status_code=400,
                            error_message=str(exc),
                        )
                        return HttpResponse.BadRequest(f"Bajaj integration failed: {str(exc)}")
                
                lead = create_lead(payload)
                _update_bank_lead_trace(
                    bank_trace,
                    lead=lead,
                    status=BankLeadTrace.Status.SUCCESS,
                    bank_lead_id=getattr(lead, "BankLeadID", None) or payload.get("BankLeadID"),
                )
            else:
                lead = create_lead(payload)

            logger.info("Create Lead Response| payload=%s", LeadCreateSerializer(lead).data)
            return HttpResponse.Success({"lead": LeadCreateSerializer(lead).data})
        except ValueError as ve:
            _update_bank_lead_trace(
                bank_trace,
                status=BankLeadTrace.Status.FAILED,
                response_status_code=400,
                error_message=str(ve),
            )
            # Extract first error message from serializer errors dict if present
            errors = ve.args[0]
            if isinstance(errors, dict):
                for field in errors:
                    if isinstance(errors[field], list) and errors[field]:
                        return HttpResponse.BadRequest(errors[field][0])
                    elif isinstance(errors[field], str):
                        return HttpResponse.BadRequest(errors[field])
            return HttpResponse.BadRequest(str(errors))
        except RuntimeError:
            return HttpErrors.InternalServerError("Failed to create lead.")


class LeadAutoClosureSettingView(APIView):
    """
    API to set or update auto-closure settings for different lead types and product subcategories.
    """

    @extend_schema(
        tags=["Onboarding V2 Settings"],
        summary="Create or update auto-closure settings",
        request=LeadAutoClosureSettingSerializer,
        responses={200: LeadAutoClosureSettingSerializer},
    )
    def post(self, request):
        try:
            serializer = LeadAutoClosureSettingSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            lead_type = serializer.validated_data["lead_type"]
            product_subcategory = serializer.validated_data["product_subcategory"]
            auto_closure_days = serializer.validated_data["auto_closure_days"]

            setting, created = LeadAutoClosureSetting.objects.update_or_create(
                lead_type=lead_type,
                product_subcategory=product_subcategory,
                defaults={"auto_closure_days": auto_closure_days, "is_active": True},
            )

            serializer = LeadAutoClosureSettingSerializer(setting)
            return HttpResponse.Success(serializer.data)
        except Exception as e:
            logger.exception("Failed to update auto-closure setting")
            return HttpErrors.InternalServerError(str(e))

    @extend_schema(
        tags=["Onboarding V2 Settings"],
        summary="Get all auto-closure settings",
        responses={200: LeadAutoClosureSettingSerializer(many=True)},
    )
    def get(self, request):
        settings = LeadAutoClosureSetting.objects.filter(is_active=True)
        serializer = LeadAutoClosureSettingSerializer(settings, many=True)
        return HttpResponse.Success(serializer.data)

    @extend_schema(
        tags=["Onboarding V2 Settings"],
        summary="Update an existing auto-closure setting",

        request=LeadAutoClosureSettingSerializer,
        responses={200: LeadAutoClosureSettingSerializer},
    )
    def patch(self, request, pk=None):
        try:
            setting_id = pk or request.data.get("id") or request.query_params.get("id")
            if not setting_id:
                return HttpResponse.BadRequest("Setting ID is required")
                
            setting = LeadAutoClosureSetting.objects.get(pk=setting_id, is_active=True)
            serializer = LeadAutoClosureSettingSerializer(setting, data=request.data, partial=True)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            serializer.save()
            return HttpResponse.Success(serializer.data)
        except LeadAutoClosureSetting.DoesNotExist:
            return HttpResponse.NotFound("Setting not found")
        except Exception as e:
            logger.exception("Failed to update auto-closure setting")
            return HttpErrors.InternalServerError(str(e))

    @extend_schema(
        tags=["Onboarding V2 Settings"],
        summary="Delete an auto-closure setting",
        responses={200: OpenApiTypes.STR},
    )
    def delete(self, request, pk=None):
        try:
            setting_id = pk or request.data.get("id") or request.query_params.get("id")
            if not setting_id:
                return HttpResponse.BadRequest("Setting ID is required")
                
            setting = LeadAutoClosureSetting.objects.get(pk=setting_id, is_active=True)
            setting.is_active = False
            setting.save(update_fields=["is_active"])
            return HttpResponse.Success("Setting deleted successfully")
        except LeadAutoClosureSetting.DoesNotExist:
            return HttpResponse.NotFound("Setting not found")
        except Exception as e:
            logger.exception("Failed to delete auto-closure setting")
            return HttpErrors.InternalServerError(str(e))



class LeadListView(APIView):
    """
    Paginated list of leads assigned to the authenticated agent.
    """

    @extend_schema(
        tags=["Onboarding V2"],
        summary="List leads with search and filter options",
        description="Returns a list of V2 leads with pagination, search, and multiple location filtering.",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, description="Search across Name, Phone, and Lead ID. Example: `John` or `9876543210`"),
            OpenApiParameter("lead_code", OpenApiTypes.STR, description="Filter by Lead ID. Example: `MPAGL0183`"),
            OpenApiParameter("customer_id", OpenApiTypes.STR, description="Filter by Customer ID. Example: `AAA0304`"),
            OpenApiParameter("contact_number", OpenApiTypes.STR, description="Filter by Phone Number. Example: `9876543210`"),
            OpenApiParameter("customer_name", OpenApiTypes.STR, description="Filter by Customer Name. Example: `John Doe`"),
            OpenApiParameter("product_category", OpenApiTypes.STR, description="Filter by Product Category. Example: `LOAN`"),
            OpenApiParameter("product_subcategory", OpenApiTypes.STR, description="Filter by Product Subcategory (comma separated for multiple). Example: `GOLD_LOAN,PERSONAL_LOAN`"),
            OpenApiParameter("pincode", OpenApiTypes.STR, description="Filter by Pincode. Example: `560001`"),
            OpenApiParameter("district", OpenApiTypes.STR, description="Filter by District (comma separated for multiple). Example: `Bangalore,Mysore`"),
            OpenApiParameter("state", OpenApiTypes.STR, description="Filter by State (comma separated for multiple). Example: `Karnataka,Tamil Nadu`"),
            OpenApiParameter("punched_by", OpenApiTypes.STR, description="Filter by Punched by (employee_id). Example: `EMP1001`"),
            OpenApiParameter("lending_partner", OpenApiTypes.STR, description="Filter by Lending Partner (comma separated for multiple). Example: `AXIS_BANK,CSB_BANK`"),
            OpenApiParameter("bank", OpenApiTypes.STR, description="Alias for lending_partner. Example: `AXIS_BANK`"),
            OpenApiParameter("status", OpenApiTypes.STR, description="Filter by Status (comma separated for multiple). UI Statuses: `Active` (mapped to ACTIVE), `Auto Close` (mapped to AUTO_CLOSED), `Application Created` (mapped to APPLICATION_CREATED). Example: `Active,Application Created`"),
            OpenApiParameter("created_on", OpenApiTypes.DATE, description="Filter by Date (YYYY-MM-DD). Example: `2024-03-25`"),
            OpenApiParameter("start_date", OpenApiTypes.DATE, description="Filter by Start Date (YYYY-MM-DD). Example: `2024-01-01`"),
            OpenApiParameter("end_date", OpenApiTypes.DATE, description="Filter by End Date (YYYY-MM-DD). Example: `2024-03-28`"),
            OpenApiParameter("lead_type", OpenApiTypes.STR, description="Filter by Lead Type (comma separated for multiple). Example: `BANK_LEAD,FRESH`"),
            OpenApiParameter("page", OpenApiTypes.INT, description="Page number"),
            OpenApiParameter("page_size", OpenApiTypes.INT, description="Page size"),
        ]
    )
    def get(self, request):
        try:
            user = request.user
            qs = filter_leads(user, request.query_params).prefetch_related("applications")

            paginator = DefaultPagination()
            v2_data = LeadCreateSerializer(qs, many=True).data

            def product_code(subcat):
                mapping = {
                    "GOLD_LOAN": "GL",
                    "PERSONAL_LOAN": "PL",
                    "HOME_LOAN": "HL",
                    "BUSINESS_LOAN": "BL",
                    "LOAN_AGAINST_PROPERTY": "LAP",
                    "WORKING_CAPITAL": "WC",
                    "OVERDRAFT_DOD": "OD",
                    "HEALTH_INSURANCE": "Insurance",
                    "MOTOR_LOAN": "ML",
                    "MOTOR_INSURANCE": "Insurance",
                    "CREDIT_CARDS": "CC",
                }
                return mapping.get(str(subcat or "").upper(), str(subcat or "UNKNOWN"))

            def product_display(item):
                code = product_code(item.get("product_subcategory"))
                lead_type = str(item.get("lead_type") or "").upper()
                if code == "GL" and lead_type:
                    type_map = {
                        "FRESH": "Fresh",
                        "BT": "Balance Transfer",
                        "BALANCE_TRANSFER": "Balance Transfer",
                        "CO_LENDING": "Co-Lending",
                        "SELF_LENDING": "Self Lending",
                        "BANK_LEAD": "Bank Lead",
                    }
                    suffix = type_map.get(lead_type, lead_type.title())
                    return f"{code}-{suffix}"
                return code

            # def with_location(item):
            #     pin = item.get("pincode")
            #     state = None
            #     district = None
            #     if pin:
            #         rec = PincodeMaster.objects.filter(pincode=pin).first()
            #         if rec:
            #             state = rec.statename
            #             district = rec.district
            #     item["state"] = state
            #     item["district"] = district
            #     return item

            v2_index = {str(l.id): l for l in qs}
            mapped_v2 = []
            for item in v2_data:
                item = dict(item)
                item["product_display"] = product_display(item)
                # item = with_location(item)
                lead_obj = v2_index.get(str(item.get("id")))

                punched_emp = ""
                punched_team = ""
                if lead_obj and getattr(lead_obj, "created_by_id", None):
                    try:
                        user_obj = getattr(lead_obj, "created_by", None)
                        if user_obj:
                            punched_emp = str(getattr(user_obj, "employee_id", "") or "")
                            punched_team = str(getattr(user_obj, "team", "") or "")
                        else:
                            u = User.objects.filter(user_id=lead_obj.created_by_id).only("employee_id", "team").first()
                            punched_emp = str(getattr(u, "employee_id", "") or "")
                            punched_team = str(getattr(u, "team", "") or "")
                    except Exception:
                        punched_emp = ""
                        punched_team = ""
                item["punched_by"] = punched_emp
                item["team"] = punched_team
                item["manager_id"] = ""
                item["source"] = "Fincom" if getattr(lead_obj, "source", None) == "AGENT" else "MoneyPal"
                item["status"] = item.get("status") or ""

                # Add requested fields
                item["product_category"] = item.get("product_category")
                item["product_subcategory"] = item.get("product_subcategory")
                item["application_id"] = item.get("application_id")
                item["parent_application_id"] = item.get("parent_application_id")
                
                # Fetch prescreen status from the latest application
                prescreen_status = False
                is_fresh_onboarding_submitted = False
                lending_partner = item.get("lending_partner") or ""
                if lead_obj:
                    latest_app = lead_obj.applications.last()
                    if latest_app:
                        prescreen_status = bool(getattr(latest_app, "saas_request_id", None))
                        is_fresh_onboarding_submitted = (
                            latest_app.loan_type == LeadType.FRESH
                            and latest_app.stage == ApplicationStage.SUBMITTED
                        )
                        lending_partner = latest_app.lending_partner or ""
                item["prescreen_status"] = prescreen_status
                item["isFreshOnboardingSubmitted"] = is_fresh_onboarding_submitted
                item["lending_partner"] = lending_partner

                mapped_v2.append(item)

            combined = mapped_v2
            page_str = request.query_params.get("page")
            page_size_str = request.query_params.get("page_size")
            try:
                page_num = int(page_str) if page_str else 1
            except ValueError:
                page_num = 1
            try:
                page_size_num = int(page_size_str) if page_size_str else DefaultPagination.page_size
            except ValueError:
                page_size_num = DefaultPagination.page_size
            total_items = len(combined)
            max_pages = math.ceil(total_items / page_size_num) if page_size_num and total_items else 1
            if page_num > max_pages:
                resp = {
                    "count": total_items,
                    "next": None,
                    "previous": None,
                    "results": {"leads": []},
                }
                return HttpResponse.Success(resp)
            try:
                page = paginator.paginate_queryset(combined, request)
                resp = paginator.get_paginated_response({"leads": page}).data
            except NotFound:
                resp = {
                    "count": total_items,
                    "next": None,
                    "previous": None,
                    "results": {"leads": []},
                }
            return HttpResponse.Success(resp)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class BTApplicationJourneyView(APIView):
    """
    Returns the journey steps and status for a Balance Transfer application.
    """

    def get(self, request, application_id):
        try:
            application = ApplicationV2.objects.select_related("lead").get(
                application_id=application_id
            )
        except ApplicationV2.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        lead = application.lead
        if lead.lead_type != LeadType.BALANCE_TRANSFER:
            return HttpResponse.BadRequest(
                "Journey API is only available for Balance Transfer applications"
            )

        # Status mapping
        # COMPLETED: Green tick
        # IN_PROGRESS: Orange tick
        # FAILED: Red tick
        # PENDING: Grey tick

        def get_status_and_remarks(label):
            status = "PENDING"
            remarks = ""
            extra = {}

            if label == "Lead Generated":
                status = "COMPLETED"
                remarks = lead.lead_code or ""
            
            elif label == "Customer ID Check":
                if lead.customer_id:
                    status = "COMPLETED"
                    remarks = lead.customer_id
                else:
                    status = "PENDING"

            elif label == "Application Created":
                status = "COMPLETED"
                remarks = application.application_id

            elif label == "Check Eligibility":
                eligible_statuses = {
                    ApplicationStatus.ELIGIBLE,
                    ApplicationStatus.PASSED,
                    ApplicationStatus.READY_FOR_LOAN,
                    ApplicationStatus.APPROVED,
                    ApplicationStatus.AGREEMENT_SIGNED,
                    ApplicationStatus.DISBURSEMENT_READY,
                    ApplicationStatus.DISBURSED,
                }
                failed_statuses = {
                    ApplicationStatus.REJECTED,
                    ApplicationStatus.NOT_ELIGIBLE,
                    ApplicationStatus.FAILED_TO_SUBMIT_PRESCREEN,
                }
                in_progress_statuses = {
                    ApplicationStatus.SENT_FOR_PRE_SCREENING,
                    ApplicationStatus.IN_PROGRESS,
                }
                
                if application.status in eligible_statuses:
                    status = "COMPLETED"
                elif application.status in failed_statuses:
                    status = "FAILED"
                elif application.status in in_progress_statuses:
                    status = "IN_PROGRESS"
                
                # Fallback: check stage snapshots
                if status in ["PENDING", "IN_PROGRESS"]:
                    if application.stage_snapshots.filter(stage__iexact=ApplicationStage.ELIGIBILITY, is_complete=True).exists():
                        status = "COMPLETED"
                
                remarks = application.saas_prescreen_remarks or ""

            elif label == "AA + BSA":
                # Placeholder for now
                status = "PENDING"

            elif label == "Onboarding":
                # If stage is beyond onboarding or status is beyond eligibility
                if application.stage in [ApplicationStage.SUBMITTED, ApplicationStage.COMPLETE]:
                    status = "COMPLETED"
                elif application.stage_snapshots.filter(is_complete=True).exists():
                    status = "IN_PROGRESS"
                
                # For BT, if Waiver or later main stages are done, onboarding is completed
                if lead.lead_type == LeadType.BALANCE_TRANSFER:
                    if application.stage_snapshots.filter(
                        stage__in=[ApplicationStage.WAIVER, ApplicationStage.CHOOSE_CUSTOMER, ApplicationStage.SUBMITTED, ApplicationStage.COMPLETE], 
                        is_complete=True
                    ).exists():
                        status = "COMPLETED"

                # If status is already beyond onboarding
                if application.status in {ApplicationStatus.APPROVED, ApplicationStatus.AGREEMENT_SIGNED, ApplicationStatus.DISBURSEMENT_READY, ApplicationStatus.DISBURSED}:
                    status = "COMPLETED"
                
                if status == "IN_PROGRESS":
                    remarks = f"Current Stage: {application.stage}"

            elif label == "Personal Discussion":
                # Check AbleCredit session or Saastech status
                # If saas_status contains something related to PD or status is beyond PD
                pd_completed_statuses = {
                    ApplicationStatus.APPROVED,
                    ApplicationStatus.AGREEMENT_SIGNED,
                    ApplicationStatus.DISBURSEMENT_READY,
                    ApplicationStatus.DISBURSED,
                }
                if application.status in pd_completed_statuses:
                    status = "COMPLETED"
                elif "AbleCredit" in (lead.metadata or {}):
                    status = "IN_PROGRESS"

            elif label == "Application Submitted":
                if application.stage == ApplicationStage.SUBMITTED or application.status not in {ApplicationStatus.DRAFT, ApplicationStatus.IN_PROGRESS, ApplicationStatus.SENT_FOR_PRE_SCREENING}:
                    status = "COMPLETED"
                remarks = f"Status: {application.status}"

            elif label == "Underwrite Approval":
                if application.status in {ApplicationStatus.APPROVED, ApplicationStatus.AGREEMENT_SIGNED, ApplicationStatus.DISBURSEMENT_READY, ApplicationStatus.DISBURSED}:
                    status = "COMPLETED"
                elif application.status == ApplicationStatus.REJECTED:
                    status = "FAILED"
                elif application.status == ApplicationStatus.CORRECTION:
                    status = "IN_PROGRESS"
                remarks = application.saas_loan_remarks or ""

            elif label == "E-Sign":
                if application.status in {ApplicationStatus.ESIGN_COMPLETED, ApplicationStatus.AGREEMENT_SIGNED, ApplicationStatus.DISBURSEMENT_READY, ApplicationStatus.DISBURSED}:
                    status = "COMPLETED"
                elif application.status in {ApplicationStatus.READY_FOR_LOAN, ApplicationStatus.ESIGN_INITIATED}:
                    status = "IN_PROGRESS"
                
                # Fetch esign_url from WebhookEvent
                event = WebhookEvent.objects.filter(
                    application_id=application.application_id,
                    payload__esign_url__isnull=False
                ).order_by("-created_at").first()
                if event:
                    extra["esign_url"] = event.payload.get("esign_url")

            elif label == "Selfie Uploaded":
                if application.documents.filter(document_type=DocumentType.LIVE_PHOTO, status="VERIFIED").exists():
                    status = "COMPLETED"
                elif application.documents.filter(document_type=DocumentType.LIVE_PHOTO).exists():
                    status = "IN_PROGRESS"

            elif label == "RH Approved":
                if application.status == ApplicationStatus.APPROVED_BY_RH or application.status in {ApplicationStatus.DISBURSEMENT_READY, ApplicationStatus.DISBURSED}:
                    status = "COMPLETED"
                elif application.status == ApplicationStatus.REJECTED_BY_RH:
                    status = "FAILED"
                elif application.status == ApplicationStatus.CORRECTION_RAISED_BY_RH:
                    status = "IN_PROGRESS"
                remarks = application.rh_remarks or ""

            elif label == "Fund Approved":
                if application.saas_status == "FUND_APPROVED" or application.status in {ApplicationStatus.DISBURSEMENT_READY, ApplicationStatus.DISBURSED}:
                    status = "COMPLETED"

            elif label == "Fund Disbursed":
                if application.status == ApplicationStatus.DISBURSED:
                    status = "COMPLETED"

            elif label == "Amount Paid to Existing Lender":
                if application.saas_status == "AMOUNT_PAID":
                    status = "COMPLETED"

            elif label == "Gold Collected":
                if application.saas_status == "GOLD_COLLECTED":
                    status = "COMPLETED"

            elif label == "Gold Pledged":
                if application.saas_status == "GOLD_PLEDGED":
                    status = "COMPLETED"

            elif label == "New Loan Updates":
                if application.saas_status == "NEW_LOAN_UPDATED":
                    status = "COMPLETED"

            elif label == "Fund Received":
                if application.saas_status == "FUND_RECEIVED":
                    status = "COMPLETED"

            return status, remarks, extra

        journey_labels = [
            "Lead Generated",
            "Customer ID Check",
            "Application Created",
            "Check Eligibility",
            "AA + BSA",
            "Onboarding",
            "Personal Discussion",
            "Application Submitted",
            "Underwrite Approval",
            "E-Sign",
            "Selfie Uploaded",
            "RH Approved",
            "Fund Approved",
            "Fund Disbursed",
            "Amount Paid to Existing Lender",
            "Gold Collected",
            "Gold Pledged",
            "New Loan Updates",
            "Fund Received",
        ]

        journey = []
        for label in journey_labels:
            status, remarks, extra = get_status_and_remarks(label)
            item = {
                "label": label,
                "status": status,
                "remarks": remarks
            }
            if extra:
                item.update(extra)
            journey.append(item)

        data = ApplicationV2Serializer(application).data
        return HttpResponse.Success({
            "application": data,
            "journey": journey
        })


class ApplicationCreateView(APIView):
    @extend_schema(
        tags=["Onboarding V2"],
        summary="Create a new application",
        description="Creates a new application for an existing lead.",
        request=ApplicationCreateSerializer,
        examples=[
            OpenApiExample(
                name="Application Create Payload",
                value={
                    "lead": "f6048bb2-4338-4056-9d35-4f23e7c13942",
                    "lending_partner": "AXIS_BANK",
                    "loan_type": "BALANCE_TRANSFER",
                },
                request_only=True,
            ),
        ],
        responses={
            200: ApplicationV2Serializer,
            400: OpenApiTypes.STR,
            500: OpenApiTypes.STR,
        },
    )
    def post(self, request):
        logger.info("Create Application Request| payload=%s", request.data)
        if request.user.role == ROLES.REGIONAL_HEAD.value:
            return HttpResponse.BadRequest("RH users are not allowed to create applications.")
        try:
            data = request.data.copy()
            lead_id = data.get("lead")

            # Enforce single application per lead
            if lead_id and ApplicationV2.objects.filter(lead_id=lead_id).exists():
                return HttpResponse.BadRequest("An application already exists for this lead.")

            lead_obj = None
            if lead_id:
                lead_obj = LeadV2.objects.filter(id=lead_id).first()
                if not lead_obj:
                    return HttpResponse.BadRequest("Lead does not exist.")
                
                if lead_obj.status == LeadStatus.AUTO_CLOSED:
                    return HttpResponse.BadRequest("Auto-closed leads are not eligible for application journey.")

            parent_lead_code = data.pop("parent_lead_code", None)
            if parent_lead_code:
                parent_lead = LeadV2.objects.filter(lead_code=parent_lead_code).first()
                if parent_lead:
                    parent_app = ApplicationV2.objects.filter(lead=parent_lead).first()
                    if parent_app:
                        data["parent_application_id"] = parent_app.application_id

            payload = prepare_application_create_data(request.user, data, lead_obj)
            from onboarding_v2 import views as views_module

            app = views_module.create_application(payload)
            
            # Update Lead status
            if lead_obj:
                lead_obj.status = LeadStatus.APPLICATION_CREATED
                lead_obj.save(update_fields=["status", "modified_at"])

            logger.info("Create Application Request| payload=%s", ApplicationV2Serializer(app).data)
            return HttpResponse.Success({"application": ApplicationV2Serializer(app).data})
        except ValueError as ve:
            return HttpResponse.BadRequest(ve.args[0])
        except Exception as exc:
            logger.exception("Application create failed")
            from onboarding_v2 import views as views_module

            views_module.notify_app_step_error("", "CREATE_APPLICATION", str(exc), payload=request.data)
            return HttpErrors.InternalServerError("Failed to create application")


class ApplicationListView(APIView):
    """
    Paginated list of applications whose leads are assigned to the authenticated agent.
    """

    @extend_schema(
        tags=["Onboarding V2"],
        summary="List applications with search and filter options",
        description="Returns paginated applications. Supports searching by Name, Application ID, Phone, and Customer ID, and filtering by Loan Type, Amount Range, Application Date (using 'application_date' or 'date'), Status, Bank/Lending Partner (using 'bank' or 'lending_partner'), and District.",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, description="Search across Customer Name, Application ID, Phone, and Customer ID. Example: `John` or `APP123`"),
            OpenApiParameter("application_id", OpenApiTypes.STR, description="Filter by Application ID. Example: `APP123`"),
            OpenApiParameter("customer_id", OpenApiTypes.STR, description="Filter by Customer ID. Example: `CUST456`"),
            OpenApiParameter("contact_number", OpenApiTypes.STR, description="Filter by Phone Number. Example: `9876543210`"),
            OpenApiParameter("customer_name", OpenApiTypes.STR, description="Filter by Customer Name. Example: `John Doe`"),
            OpenApiParameter("loan_type", OpenApiTypes.STR, description="Filter by Loan Type (comma separated for multiple). Example: `GOLD_LOAN,PERSONAL_LOAN`"),
            OpenApiParameter("amount_range", OpenApiTypes.STR, description="Filter by Amount Range. Formats: `min-max` or `min+`. Example: `0-200000`, `200001-500000`, `1000000+`"),
            OpenApiParameter("application_date", OpenApiTypes.DATE, description="Filter by Application Date (YYYY-MM-DD). Example: `2024-03-25`"),
            OpenApiParameter("date", OpenApiTypes.DATE, description="Filter by Application Date (YYYY-MM-DD). Example: `2024-03-25`"),
            OpenApiParameter("start_date", OpenApiTypes.DATE, description="Filter by Start Date (YYYY-MM-DD). Example: `2024-01-01`"),
            OpenApiParameter("end_date", OpenApiTypes.DATE, description="Filter by End Date (YYYY-MM-DD). Example: `2024-03-31`"),
            OpenApiParameter("status", OpenApiTypes.STR, description="Filter by Status (comma separated for multiple). Example: `DRAFT,IN_PROGRESS`"),
            OpenApiParameter("bank", OpenApiTypes.STR, description="Filter by Bank (Lending Partner) (comma separated for multiple). Example: `HDFC,ABCL`"),
            OpenApiParameter("lending_partner", OpenApiTypes.STR, description="Filter by Lending Partner (comma separated for multiple). Example: `HDFC,ABCL`"),
            OpenApiParameter("district", OpenApiTypes.STR, description="Filter by District (comma separated for multiple). Example: `Bangalore,Mysore`"),
            OpenApiParameter("lead_type", OpenApiTypes.STR, description="Filter by Lead Type (comma separated for multiple). Example: `BANK_LEAD,FRESH`"),
            OpenApiParameter("page", OpenApiTypes.INT, description="Page number"),
            OpenApiParameter("page_size", OpenApiTypes.INT, description="Page size"),
        ]
    )
    def get(self, request):
        qs = (
            filter_applications(request.user, request.query_params)
            .select_related("lead")
            .prefetch_related("bank_details", "stage_snapshots", "punched_loans")
        )
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = ApplicationListSerializer(page, many=True)
        return paginator.get_paginated_response({"applications": serializer.data})


class OnboardingDashboardView(APIView):
    def get(self, request):
        leads_qs = filter_leads(request.user, request.query_params)
        applications_qs = (
            filter_applications(request.user, request.query_params)
            .select_related("lead")
            .prefetch_related("bank_details", "stage_snapshots", "punched_loans")
        )
        metrics = {
            "total_leads": leads_qs.count(),
            "total_applications": applications_qs.count(),
            "active_agents": User.objects.filter(role=ROLES.AGENT.value, is_active=True).count(),
        }
        paginator = DefaultPagination()
        page = paginator.paginate_queryset(applications_qs, request)
        serializer = ApplicationListSerializer(page, many=True)
        in_progress_qs = applications_qs.filter(
            status__in=[
                ApplicationStatus.DRAFT,
                ApplicationStatus.SENT_FOR_PRE_SCREENING,
                ApplicationStatus.IN_PROGRESS,
                ApplicationStatus.READY_FOR_LOAN,
            ]
        ).order_by("-created_at")
        in_progress_ser = ApplicationListSerializer(in_progress_qs, many=True)
        agents_qs = User.objects.filter(role=ROLES.AGENT.value, is_active=True).order_by("first_name", "last_name")
        agents_ser = UserResponseSerializer(agents_qs, many=True)
        payload = {
            "metrics": metrics,
            "total_earning": None,
            "tasks": None,
            "applications": serializer.data,
            "in_progress_applications": in_progress_ser.data,
            "agents": agents_ser.data,
        }
        return paginator.get_paginated_response(payload)
