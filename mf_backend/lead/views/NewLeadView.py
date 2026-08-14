from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from utils.responseHandler import HttpResponse
from lead.models import NewLead
from lead.serializers import NewLeadSerializer
import traceback
from utils.common import generate_lead_id
from utils.constants import NEW_LEAD_STATUS, ROLES
from onboarding_v2.constants import LeadSource
from onboarding_v2.serializers import LeadCreateSerializer
from onboarding_v2.helpers.lead_application_helpers import filter_leads
from onboarding_v2.views.common import DefaultPagination
from onboarding_v2.models import LeadV2, PincodeMaster
from rest_framework.exceptions import NotFound
import math
import uuid
from django.db.models import Q
from users.models import User


class NewLeadView(APIView):
    def post(self, request):
        try:
            data = request.data
            user = request.user
            loan_type = data.get("loan_type")
            data["lead_id"] = generate_lead_id(loan_type)
            data["created_by"] = user.user_id
            data["modified_by"] = user.user_id
            serializer = NewLeadSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"lead": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    @extend_schema(
        tags=["Leads"],
        summary="List new leads with search and filter options",
        description="Returns a list of V2 leads with search, location, and agent filters.",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, description="Search across Name, Phone, and Lead ID. Example: `John` or `9876543210`"),
            OpenApiParameter("lead_code", OpenApiTypes.STR, description="Filter by Lead ID. Example: `MPAGL0183`"),
            OpenApiParameter("contact_number", OpenApiTypes.STR, description="Filter by Phone Number. Example: `9876543210`"),
            OpenApiParameter("customer_name", OpenApiTypes.STR, description="Filter by Customer Name. Example: `John Doe`"),
            OpenApiParameter("product_category", OpenApiTypes.STR, description="Filter by Product Category. Example: `LOAN`"),
            OpenApiParameter("product_subcategory", OpenApiTypes.STR, description="Filter by Product Subcategory (comma separated for multiple). Example: `GOLD_LOAN,PERSONAL_LOAN`"),
            OpenApiParameter("pincode", OpenApiTypes.STR, description="Filter by Pincode. Example: `560001`"),
            OpenApiParameter("district", OpenApiTypes.STR, description="Filter by District (comma separated for multiple). Example: `Bangalore,Mysore`"),
            OpenApiParameter("state", OpenApiTypes.STR, description="Filter by State (comma separated for multiple). Example: `Karnataka,Tamil Nadu`"),
            OpenApiParameter("punched_by", OpenApiTypes.STR, description="Filter by Punched by (employee_id). Example: `EMP1001`"),
            OpenApiParameter("source", OpenApiTypes.STR, description="Filter by Source. Example: `MoneyPal`"),
            OpenApiParameter("status", OpenApiTypes.STR, description="Filter by Status (comma separated for multiple). UI Statuses: `Active` (mapped to ACTIVE), `Auto Close` (mapped to AUTO_CLOSED), `Application Created` (mapped to APPLICATION_CREATED). Example: `Active,Application Created`"),
            OpenApiParameter("created_on", OpenApiTypes.DATE, description="Filter by Date (YYYY-MM-DD). Example: `2024-03-25`"),
            OpenApiParameter("start_date", OpenApiTypes.DATE, description="Filter by Start Date (YYYY-MM-DD). Example: `2024-01-01`"),
            OpenApiParameter("end_date", OpenApiTypes.DATE, description="Filter by End Date (YYYY-MM-DD). Example: `2024-03-28`"),
            OpenApiParameter("agent_id", OpenApiTypes.STR, description="Filter by Agent User ID. Example: `550e8400-e29b-41d4-a716-446655440000`"),
            OpenApiParameter("employee_id", OpenApiTypes.STR, description="Filter by Agent Employee ID. Example: `EMP1001`"),
            OpenApiParameter("page", OpenApiTypes.INT, description="Page number"),
            OpenApiParameter("page_size", OpenApiTypes.INT, description="Page size"),
        ]
    )
    def get(self, request):
        try:
            lead_id = request.GET.get("lead_id")
            new_lead_id = request.GET.get("new_lead_id")
            agent_id = request.GET.get("agent_id")
            employee_id = request.GET.get("employee_id")
            if not agent_id and employee_id:
                u = User.objects.filter(employee_id=employee_id).only("user_id").first()
                agent_id = str(getattr(u, "user_id", "")) if u else None
            lookup_lead_id = lead_id or new_lead_id
            if lookup_lead_id:
                lead = (
                    LeadV2.objects.filter(id=lookup_lead_id)
                    .prefetch_related("applications")
                    .first()
                )
                if not lead:
                    return HttpResponse.BadRequest("Lead not found")
                return HttpResponse.Success({"lead": LeadCreateSerializer(lead).data})
            qs = filter_leads(
                request.user, request.query_params, all_users=True
            ).prefetch_related("applications")

            # Scope listing results for Tele roles
            user = request.user
            if user.role == ROLES.TELE_ADMIN.value:
                if getattr(user, 'team', None):
                    team_member_ids = list(
                        User.objects.filter(team=user.team).values_list('user_id', flat=True)
                    )
                else:
                    team_member_ids = [user.user_id]
                qs = qs.filter(Q(created_by_id__in=team_member_ids) | Q(assigned_to_id=user.user_id))
            elif user.role == ROLES.TELE_USER.value:
                qs = qs.filter(Q(created_by_id=user.user_id) | Q(assigned_to_id=user.user_id))

            if agent_id:
                is_uuid = False
                try:
                    uuid.UUID(str(agent_id))
                    is_uuid = True
                except (ValueError, AttributeError):
                    is_uuid = False
                
                if is_uuid:
                    qs = qs.filter(Q(created_by_id=agent_id) | Q(assigned_to_id=agent_id))
                else:
                    # If not a UUID, filter by employee_id
                    qs = qs.filter(Q(created_by__employee_id__iexact=agent_id) | Q(assigned_to__employee_id__iexact=agent_id))

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
                    }
                    suffix = type_map.get(lead_type, lead_type.title())
                    return f"{code}-{suffix}"
                return code

            def with_location(item):
                pin = item.get("pincode")
                state = None
                district = None
                if pin:
                    rec = PincodeMaster.objects.filter(pincode=pin).first()
                    if rec:
                        state = rec.statename
                        district = rec.district
                item["state"] = state
                item["district"] = district
                return item

            v2_index = {str(l.id): l for l in qs}
            mapped_v2 = []
            for item in v2_data:
                item = dict(item)
                item["product_display"] = product_display(item)
                item = with_location(item)
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
                mapped_v2.append(item)

            combined = mapped_v2
            page_str = request.query_params.get("page")
            page_size_str = request.query_params.get("limit") or request.query_params.get("page_size")
            try:
                page_num = int(page_str) if page_str else 1
            except ValueError:
                page_num = 1
            try:
                page_size_num = int(page_size_str) if page_size_str else 10
            except ValueError:
                page_size_num = 10
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
                paginator.page_size_query_param = "limit"
                paginator.page_size = page_size_num
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

    def patch(self, request):
        try:
            lead_id = request.GET.get("lead_id")
            lead = NewLead.objects.get(new_lead_id=lead_id)
            serializer = NewLeadSerializer(lead, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"lead": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except NewLead.DoesNotExist:
            return HttpResponse.BadRequest("Lead not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def delete(self, request):
        try:
            lead_id = request.GET.get("lead_id")
            NewLead.objects.get(new_lead_id=lead_id).delete()
            return HttpResponse.Success({"msg": "Lead deleted"})
        except NewLead.DoesNotExist:
            return HttpResponse.BadRequest("Lead not found")
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))


class UserNewLeadView(APIView):
    def post(self, request):
        try:
            data = request.data
            loan_type = data.get("loan_type")
            data["lead_id"] = generate_lead_id(loan_type)
            data["source_type"] = "SELF"
            serializer = NewLeadSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"lead": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class NewLeadDashboardView(APIView):
    def get(self, request):
        user = request.user
        user_leads = NewLead.objects.filter(created_by=user)
        total_leads = user_leads.count()
        in_progress_leads = user_leads.filter(status=NEW_LEAD_STATUS.IN_PROGRESS.value).count()
        disbursed_leads = user_leads.filter(status=NEW_LEAD_STATUS.DISBURSED.value).count()
        return HttpResponse.Success({
            "dashboard": {
                "total_leads": total_leads,
                "in_progress_leads": in_progress_leads,
                "disbursed_leads": disbursed_leads
            }
        })


class MyNewLeadListView(APIView):
    @extend_schema(
        tags=["Leads"],
        summary="List my leads with search and filter options",
        description="Returns a list of V2 agent-source leads for the authenticated user with search and location filters.",
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, description="Search across Name, Phone, and Lead ID. Example: `John` or `9876543210`"),
            OpenApiParameter("lead_code", OpenApiTypes.STR, description="Filter by Lead ID. Example: `MPAGL0183`"),
            OpenApiParameter("contact_number", OpenApiTypes.STR, description="Filter by Phone Number. Example: `9876543210`"),
            OpenApiParameter("customer_name", OpenApiTypes.STR, description="Filter by Customer Name. Example: `John Doe`"),
            OpenApiParameter("product_category", OpenApiTypes.STR, description="Filter by Product Category. Example: `LOAN`"),
            OpenApiParameter("product_subcategory", OpenApiTypes.STR, description="Filter by Product Subcategory (comma separated for multiple). Example: `GOLD_LOAN,PERSONAL_LOAN`"),
            OpenApiParameter("pincode", OpenApiTypes.STR, description="Filter by Pincode. Example: `560001`"),
            OpenApiParameter("district", OpenApiTypes.STR, description="Filter by District (comma separated for multiple). Example: `Bangalore,Mysore`"),
            OpenApiParameter("state", OpenApiTypes.STR, description="Filter by State (comma separated for multiple). Example: `Karnataka,Tamil Nadu`"),
            OpenApiParameter("punched_by", OpenApiTypes.STR, description="Filter by Punched by (employee_id). Example: `EMP1001`"),
            OpenApiParameter("status", OpenApiTypes.STR, description="Filter by Status (comma separated for multiple). UI Statuses: `Active` (mapped to ACTIVE), `Auto Close` (mapped to AUTO_CLOSED), `Application Created` (mapped to APPLICATION_CREATED). Example: `Active,Application Created`"),
            OpenApiParameter("created_on", OpenApiTypes.DATE, description="Filter by Date (YYYY-MM-DD). Example: `2024-03-25`"),
            OpenApiParameter("start_date", OpenApiTypes.DATE, description="Filter by Start Date (YYYY-MM-DD). Example: `2024-01-01`"),
            OpenApiParameter("end_date", OpenApiTypes.DATE, description="Filter by End Date (YYYY-MM-DD). Example: `2024-03-28`"),
            OpenApiParameter("page", OpenApiTypes.INT, description="Page number"),
            OpenApiParameter("page_size", OpenApiTypes.INT, description="Page size"),
        ]
    )
    def get(self, request):
        query_params = request.query_params.copy()
        query_params.pop("source", None)
        qs = (
            filter_leads(request.user, query_params, all_users=True)
            .filter(
                Q(created_by=request.user) | Q(assigned_to=request.user),
                source=LeadSource.AGENT,
            )
            .select_related("created_by", "assigned_to")
            .prefetch_related("applications")
        )
        paginator = DefaultPagination()
        paginator.page_size_query_param = "limit"
        limit_val = request.query_params.get("limit") or request.query_params.get("page_size")
        if limit_val and limit_val.isdigit():
            paginator.page_size = int(limit_val)
        else:
            paginator.page_size = 10
        page = paginator.paginate_queryset(qs, request)
        raw = LeadCreateSerializer(page, many=True).data

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
                }
                suffix = type_map.get(lead_type, lead_type.title())
                return f"{code}-{suffix}"
            return code

        def with_location(item):
            pin = item.get("pincode")
            state = None
            district = None
            if pin:
                rec = PincodeMaster.objects.filter(pincode=pin).first()
                if rec:
                    state = rec.statename
                    district = rec.district
            item["state"] = state
            item["district"] = district
            return item

        lead_index = {str(lead.id): lead for lead in page}

        enriched = []
        for item in raw:
            x = dict(item)
            x["product_display"] = product_display(x)
            lead_obj = lead_index.get(str(x.get("id")))
            punched_by = ""
            punched_team = ""
            if lead_obj and getattr(lead_obj, "created_by_id", None):
                user_obj = getattr(lead_obj, "created_by", None)
                if user_obj:
                    punched_by = str(getattr(user_obj, "employee_id", "") or "")
                    punched_team = str(getattr(user_obj, "team", "") or "")
            x["punched_by"] = punched_by
            x["team"] = punched_team
            x["manager_id"] = ""
            x["source"] = "Fincom"
            x["loan_application_id"] = None
            x["loan_account_number"] = None
            x["disbursed_amount"] = None
            x["disbursed_on_date"] = None
            x = with_location(x)
            enriched.append(x)

        resp = paginator.get_paginated_response({"leads": enriched}).data
        return HttpResponse.Success(resp)
