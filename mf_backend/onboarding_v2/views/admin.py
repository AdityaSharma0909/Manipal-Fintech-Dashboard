import uuid
from datetime import timedelta

from django.apps import apps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import logging
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema

from utils.responseHandler import HttpResponse
from onboarding_v2.constants import ProductSubCategory
from onboarding_v2.models import (
    BankBranch,
    BankDetailsV2,
    DailyGoldRate,
    LendingPartnerMaster,
    PincodeMaster,
    ThirdPartyLender,
    CustomerBankAccount,
    RoiConfiguration,
)
from onboarding_v2.serializers.bank import (
    BankBranchSerializer,
    BankBranchListSerializer,
    BankBranchCreateSerializer,
    LendingPartnerMasterSerializer,
    CustomerBankAccountSerializer,
)
from onboarding_v2.serializers.daily_gold_rate import DailyGoldRateSerializer, HistoricalDailyGoldRateSerializer
from onboarding_v2.serializers.pincode import PincodeSerializer
from onboarding_v2.serializers.third_party_lender import ThirdPartyLenderSerializer
from onboarding_v2.serializers.roi_configuration import RoiConfigurationSerializer
from onboarding_v2.serializers import (
    ImportBranchFileSerializer,
    ImportPincodeFileSerializer,
)
from onboarding_v2.tasks import import_bank_branches_task, import_pincodes_task

log = logging.getLogger('logs')

class BankBranchListCreateView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        operation_id="onboarding_v2_bank_branches_list",
        summary="List or search bank branches",
        parameters=[
            OpenApiParameter("bank_name", OpenApiTypes.STR, description="Filter by bank name"),
            OpenApiParameter("ifsc_code", OpenApiTypes.STR, description="Filter by IFSC code"),
            OpenApiParameter("branch_name", OpenApiTypes.STR, description="Filter by branch name"),
            OpenApiParameter("city", OpenApiTypes.STR, description="Filter by city"),
            OpenApiParameter("state", OpenApiTypes.STR, description="Filter by state"),
            OpenApiParameter("district", OpenApiTypes.STR, description="Filter by district"),
            OpenApiParameter("pincode", OpenApiTypes.STR, description="Filter by pincode"),
            OpenApiParameter("search", OpenApiTypes.STR, description="Search across multiple fields (bank_name, branch_name, ifsc_code, city, state, district, pincode)"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        qs = BankBranch.objects.all()
        
        search_query = request.query_params.get("search")
        if search_query:
            qs = qs.filter(
                Q(bank_name__icontains=search_query) |
                Q(branch_name__icontains=search_query) |
                Q(ifsc_code__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(state__icontains=search_query) |
                Q(district__icontains=search_query) |
                Q(pincode__icontains=search_query)
            )

        bank_name = request.query_params.get("bank_name")
        if bank_name:
            qs = qs.filter(bank_name__iexact=bank_name)
        lender_code = request.query_params.get("lender_code")
        if lender_code:
            qs = qs.filter(lender__lender_code=lender_code)
        # Field-wise filters
        branch_name = request.query_params.get("branch_name")
        if branch_name:
            qs = qs.filter(branch_name__icontains=branch_name)
        ifsc_code = request.query_params.get("ifsc_code")
        if ifsc_code:
            qs = qs.filter(ifsc_code__iexact=ifsc_code)
        sol_id = request.query_params.get("sol_id")
        if sol_id:
            qs = qs.filter(sol_id__iexact=sol_id)
        glo_id = request.query_params.get("glo_id")
        if glo_id:
            qs = qs.filter(glo_id__iexact=glo_id)
        glo_name = request.query_params.get("glo_name")
        if glo_name:
            qs = qs.filter(glo_name__icontains=glo_name)
        agent_id = request.query_params.get("agent_id")
        if agent_id:
            qs = qs.filter(agent_id__iexact=agent_id)
        agent_name = request.query_params.get("agent_name")
        if agent_name:
            qs = qs.filter(agent_name__icontains=agent_name)
        agent_status = request.query_params.get("agent_wise_status")
        if agent_status:
            qs = qs.filter(agent_wise_status__icontains=agent_status)
        city = request.query_params.get("city")
        if city:
            qs = qs.filter(city__icontains=city)
        state = request.query_params.get("state")
        if state:
            qs = qs.filter(state__icontains=state)
        district = request.query_params.get("district")
        if district:
            qs = qs.filter(district__icontains=district)
        correct_district = request.query_params.get("correct_district")
        if correct_district:
            qs = qs.filter(correct_district__icontains=correct_district)
        pincode = request.query_params.get("pincode")
        if pincode:
            qs = qs.filter(pincode__iexact=pincode)
        branch_code = request.query_params.get("branch_code")
        if branch_code:
            qs = qs.filter(branch_code__iexact=branch_code)
        paginator = PageNumberPagination()
        paginator.page_size = 50
        paginator.page_size_query_param = "page_size"
        paginator.max_page_size = 200
        total_count = qs.count()
        page = paginator.paginate_queryset(qs.order_by("-created_at", "bank_name", "branch_name"), request)
        serializer = BankBranchListSerializer(page, many=True)
        return HttpResponse.Success(
            {
                "count": total_count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data,
            }
        )

    def post(self, request):
        # 1. Handle File Upload (Bulk)
        file_obj = request.FILES.get("file") or request.data.get("file")
        if file_obj and hasattr(file_obj, "read"):
            truncate = str(request.data.get("truncate", "false")).lower() == "true"
            lender_code = request.data.get("lender_code")
            bank_name = request.data.get("bank_name")
            try:
                tmp_name = f"imports/branches/{uuid.uuid4()}_{file_obj.name}"
                stored_path = default_storage.save(tmp_name, ContentFile(file_obj.read()))
                # Run synchronously to fulfill immediate request
                result = import_bank_branches_task(
                    stored_path, truncate=truncate, lender_code=lender_code, bank_name=bank_name
                )
                return HttpResponse.Success({"message": "Branch import completed", "result": result})
            except Exception as exc:
                return HttpResponse.InternalServerError(str(exc))

        # 2. Handle List-based JSON (Bulk)
        if isinstance(request.data, list):
            serializer = BankBranchSerializer(data=request.data, many=True)
            if serializer.is_valid():
                branches = serializer.save()
                return HttpResponse.Success({
                    "message": f"Successfully created {len(branches)} branches",
                    "count": len(branches),
                    "results": BankBranchSerializer(branches, many=True).data
                })
            return HttpResponse.BadRequest(serializer.errors)

        # 3. Handle Single Record JSON — use create serializer (enforces mandatory fields)
        serializer = BankBranchCreateSerializer(data=request.data)
        if serializer.is_valid():
            branch = serializer.save()
            return HttpResponse.Success({"branch": BankBranchSerializer(branch).data})
        return HttpResponse.BadRequest(serializer.errors)


class BankBranchFilterView(APIView):
    @extend_schema(
        summary="Filter bank branches",
        description=(
            "Filter bank branches by one or more fields. "
            "At least one query parameter is required."
        ),
        parameters=[
            OpenApiParameter(
                name="bank_name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Exact bank name match (case-insensitive).",
            ),
            OpenApiParameter(
                name="state",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Exact state name match (case-insensitive).",
            ),
            OpenApiParameter(
                name="district",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Exact district name match (case-insensitive).",
            ),
            OpenApiParameter(
                name="branch_name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Partial branch name match (case-insensitive).",
            ),
            OpenApiParameter(
                name="pincode",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Exact pincode match (case-insensitive).",
            ),
        ],
    )
    def get(self, request):
        bank_name = request.query_params.get("bank_name")
        state = request.query_params.get("state")
        district = request.query_params.get("district")
        branch_name = request.query_params.get("branch_name")
        pincode = request.query_params.get("pincode")

        if not any([bank_name, state, district, branch_name, pincode]):
            return HttpResponse.BadRequest(
                "At least one query param is required: bank_name, state, district, branch_name, pincode"
            )

        filters = {}
        if bank_name:
            filters["bank_name__iexact"] = bank_name.strip()
        if state:
            filters["state__iexact"] = state.strip()
        if district:
            filters["district__iexact"] = district.strip()
        if branch_name:
            filters["branch_name__icontains"] = branch_name.strip()
        if pincode:
            filters["pincode__iexact"] = pincode.strip()

        qs = BankBranch.objects.filter(**filters).order_by("bank_name", "branch_name")
        serializer = BankBranchSerializer(qs, many=True)
        return HttpResponse.Success({
            "count": qs.count(),
            "results": serializer.data,
        })


class BankBranchDetailView(APIView):
    def get_object(self, branch_id):
        try:
            return BankBranch.objects.get(id=branch_id)
        except BankBranch.DoesNotExist:
            return None

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        operation_id="onboarding_v2_bank_branch_retrieve",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request, branch_id):
        branch = self.get_object(branch_id)
        if not branch:
            return HttpResponse.BadRequest("Branch not found")
        return HttpResponse.Success({"branch": BankBranchSerializer(branch).data})

    def patch(self, request, branch_id):
        branch = self.get_object(branch_id)
        if not branch:
            return HttpResponse.BadRequest("Branch not found")
        serializer = BankBranchSerializer(branch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return HttpResponse.Success({"branch": serializer.data})
        return HttpResponse.BadRequest(serializer.errors)

    def delete(self, request, branch_id):
        branch = self.get_object(branch_id)
        if not branch:
            return HttpResponse.BadRequest("Branch not found")
        branch.delete()
        return HttpResponse.Success({"message": "Branch deleted"})


class PincodeDetailView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        operation_id="onboarding_v2_pincode_retrieve",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request, pincode):
        try:
            record = PincodeMaster.objects.get(pincode=pincode)
        except PincodeMaster.DoesNotExist:
            return HttpResponse.BadRequest("Pincode not found")
        return HttpResponse.Success({"pincode": PincodeSerializer(record).data})


class PincodeListView(APIView):
    """
    Paginated list of pincodes.
    """

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        operation_id="onboarding_v2_pincodes_list",
        summary="List pincodes",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        qs = PincodeMaster.objects.all().order_by("pincode")
        paginator = PageNumberPagination()
        paginator.page_size = 50
        paginator.page_size_query_param = "page_size"
        paginator.max_page_size = 200
        page = paginator.paginate_queryset(qs, request)
        data = PincodeSerializer(page, many=True).data
        return HttpResponse.Success(
            {
                "count": qs.count(),
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": data,
            }
        )


class AdminImportPincodesView(APIView):
    """
    Admin-only import of pincodes via CSV/XLSX.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not request.user.is_staff:
            return HttpResponse.BadRequest("Forbidden")
        serializer = ImportPincodeFileSerializer(data=request.data)
        if not serializer.is_valid():
            return HttpResponse.BadRequest(serializer.errors)
        file_obj = serializer.validated_data["file"]
        truncate = serializer.validated_data.get("truncate", False)
        try:
            tmp_name = f"imports/pincodes/{uuid.uuid4()}_{file_obj.name}"
            stored_path = default_storage.save(tmp_name, ContentFile(file_obj.read()))
            task = import_pincodes_task.delay(stored_path, truncate=truncate)
        except Exception as exc:
            return HttpResponse.InternalServerError(str(exc))
        return HttpResponse.Accepted({"task_id": str(task.id), "message": "Pincode import queued"})


class AdminImportBranchesView(APIView):
    """
    Admin-only import of bank branches via CSV/XLSX.
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not request.user.is_staff:
            return HttpResponse.BadRequest("Forbidden")
        serializer = ImportBranchFileSerializer(data=request.data)
        if not serializer.is_valid():
            return HttpResponse.BadRequest(serializer.errors)
        file_obj = serializer.validated_data["file"]
        truncate = serializer.validated_data.get("truncate", False)
        lender_code = serializer.validated_data.get("lender_code")
        bank_name = serializer.validated_data.get("bank_name")
        try:
            tmp_name = f"imports/branches/{uuid.uuid4()}_{file_obj.name}"
            stored_path = default_storage.save(tmp_name, ContentFile(file_obj.read()))
            # Run synchronously to bypass celery Kombu 'EntryPoints' issues 
            result = import_bank_branches_task(
                stored_path, truncate=truncate, lender_code=lender_code, bank_name=bank_name
            )
        except Exception as exc:
            import traceback
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(exc))
        return HttpResponse.Success({"message": "Branch import completed", "result": result})


class UniqueBankListView(APIView):
    """
    Returns a list of unique bank names from BankBranch.
    """

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Get unique bank names",
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        bank_names = (
            BankBranch.objects.exclude(bank_name__isnull=True)
            .exclude(bank_name__exact="")
            .values_list("bank_name", flat=True)
            .distinct()
            .order_by("bank_name")
        )
        return HttpResponse.Success({"banks": list(bank_names), "count": len(bank_names)})


class LendingPartnerListCreateView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="List lending partners or get details",
        description="Fetch a list of lending partners. You can filter by bank_name, available_for, and available_for_lead_type. To fetch details of a specific partner, provide the partner_id in the query parameters.",
        parameters=[
            OpenApiParameter("partner_id", OpenApiTypes.UUID, description="Fetch a specific partner by ID"),
            OpenApiParameter("bank_name", OpenApiTypes.STR, description="Filter by bank name"),
            OpenApiParameter(
                "available_for",
                OpenApiTypes.STR,
                description="Filter by product subcategory, for example GOLD_LOAN or PERSONAL_LOAN. Use NON_GOLD_LOAN to exclude GOLD_LOAN partners.",
            ),
            OpenApiParameter(
                "available_for_lead_type",
                OpenApiTypes.STR,
                description="Filter by lead type, for example CO_LENDING, FRESH, BALANCE_TRANSFER, or SELF_LENDING.",
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        partner_id = request.query_params.get("partner_id")
        if partner_id:
            try:
                partner = LendingPartnerMaster.objects.get(id=partner_id)
                return HttpResponse.Success({"lending_partner": LendingPartnerMasterSerializer(partner).data})
            except LendingPartnerMaster.DoesNotExist:
                return HttpResponse.BadRequest("Lending partner not found")

        qs = LendingPartnerMaster.objects.all()
        bank_name = request.query_params.get("bank_name")
        if bank_name:
            qs = qs.filter(bank_name__icontains=bank_name.strip())
        available_for = request.query_params.get("available_for")
        if available_for:
            normalized_available_for = available_for.strip().upper()
            if normalized_available_for == "NON_GOLD_LOAN":
                qs = qs.exclude(available_for=ProductSubCategory.GOLD_LOAN)
            else:
                qs = qs.filter(available_for__iexact=normalized_available_for)
        available_for_lead_type = request.query_params.get("available_for_lead_type")
        if available_for_lead_type:
            qs = qs.filter(
                available_for_lead_type__contains=[
                    available_for_lead_type.strip().upper()
                ]
            )

        qs = qs.order_by("bank_name", "available_for")
        serializer = LendingPartnerMasterSerializer(qs, many=True)
        return HttpResponse.Success({"count": qs.count(), "results": serializer.data})

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Create lending partner",
        description="Create one or multiple new lending partners. You can pass a single JSON object to create one partner, or a list of JSON objects to perform a bulk creation.",
        request=LendingPartnerMasterSerializer,
        examples=[
            OpenApiExample(
                "Create gold loan partner",
                value={
                    "bank_name": "Axis Bank",
                    "available_for": "GOLD_LOAN",
                    "available_for_lead_type": [
                        "CO_LENDING",
                        "FRESH",
                        "BALANCE_TRANSFER",
                        "SELF_LENDING",
                    ],
                },
                request_only=True,
            ),
            OpenApiExample(
                "Create personal loan partner",
                value={
                    "bank_name": "HDFC Bank",
                    "available_for": "PERSONAL_LOAN",
                },
                request_only=True,
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        if isinstance(request.data, list):
            serializer = LendingPartnerMasterSerializer(data=request.data, many=True)
            if serializer.is_valid():
                partners = serializer.save()
                return HttpResponse.Success(
                    {
                        "message": f"Successfully created {len(partners)} lending partners",
                        "count": len(partners),
                        "results": LendingPartnerMasterSerializer(partners, many=True).data,
                    }
                )
            return HttpResponse.BadRequest(serializer.errors)

        serializer = LendingPartnerMasterSerializer(data=request.data)
        if serializer.is_valid():
            partner = serializer.save()
            return HttpResponse.Success({"lending_partner": LendingPartnerMasterSerializer(partner).data})
        return HttpResponse.BadRequest(serializer.errors)

class LendingPartnerDetailView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Update lending partner",
        description="Update an existing lending partner's details. Only the fields provided in the payload will be updated (partial update). The partner ID must be passed in the URL.",
        request=LendingPartnerMasterSerializer,
        examples=[
            OpenApiExample(
                "Update bank rate",
                value={
                    "bank_rate": 9.2,
                },
                request_only=True,
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def patch(self, request, partner_id):
        try:
            partner = LendingPartnerMaster.objects.get(id=partner_id)
            serializer = LendingPartnerMasterSerializer(partner, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"lending_partner": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except LendingPartnerMaster.DoesNotExist:
            return HttpResponse.BadRequest("Lending partner not found")

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Delete lending partner",
        description="Permanently delete a lending partner by their ID passed in the URL.",
        responses={200: OpenApiTypes.OBJECT},
    )
    def delete(self, request, partner_id):
        try:
            partner = LendingPartnerMaster.objects.get(id=partner_id)
            partner.delete()
            return HttpResponse.Success({"message": "Lending partner deleted"})
        except LendingPartnerMaster.DoesNotExist:
            return HttpResponse.BadRequest("Lending partner not found")


class DistrictListView(APIView):
    """
    Returns a list of unique district names from PincodeMaster.
    Optionally filters by state via the 'state' query parameter.
    """

    @extend_schema(
        summary="Get unique districts",
        description=(
            "Returns a flat list of unique district names. "
            "Optionally pass a 'state' query parameter to fetch exactly the districts belonging to that specific state (e.g. for dependent dropdowns). "
            "Or pass a 'states' query parameter (comma-separated) to filter by multiple states."
        ),
        parameters=[
            OpenApiParameter(
                name="state",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="State name to filter districts by (e.g., 'Maharashtra', 'Karnataka').",
            ),
            OpenApiParameter(
                name="states",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Comma-separated state names to filter districts by (e.g., 'Maharashtra,Delhi').",
            ),
        ],
    )
    def get(self, request):
        qs = (
            PincodeMaster.objects.exclude(district__isnull=True)
            .exclude(district__exact="")
            .exclude(statename__isnull=True)
            .exclude(statename__exact="")
        )

        # Support both 'state' (single) and 'states' (comma-separated)
        states_param = request.query_params.get("states")
        state_param = request.query_params.get("state")
        states = []
        if states_param:
            # Split by comma, strip whitespace, ignore empty
            states = [s.strip() for s in states_param.split(",") if s.strip()]
        elif state_param:
            states = [state_param.strip()]

        if states:
            # Case-insensitive filter for each state using iexact Q objects
            from django.db.models import Q
            state_q = Q()
            for s in states:
                state_q |= Q(statename__iexact=s)
            qs = qs.filter(state_q)

        raw_districts = qs.values_list("district", flat=True)

        # Aggressive deduplication avoiding case/space mismatches across db entries
        unique_set = set()
        districts = []
        for d in raw_districts:
            cleaned = d.strip().title()
            if cleaned not in unique_set:
                unique_set.add(cleaned)
                districts.append(cleaned)

        districts.sort()

        return HttpResponse.Success({"districts": districts, "count": len(districts)})


class PincodeBranchLookupView(APIView):
    """
    Lookup bank branches by pincode (and optionally bank name):
    1. Get district from PincodeMaster using pincode
    2. If bank_name is provided: return branches for that district + bank
    3. If bank_name not provided: return district + unique banks for that district
    """

    @extend_schema(
        summary="Lookup branches by pincode",
        description=(
            "Lookup bank branches by pincode. "
            "Step 1: Provide pincode to get district and unique banks for that district. "
            "Step 2: Provide pincode + bank_name to get all branches for that district + bank."
        ),
        parameters=[
            OpenApiParameter(
                name="pincode",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Pincode to lookup district",
            ),
            OpenApiParameter(
                name="bank_name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Optional: Bank name to filter branches",
            ),
        ],
    )
    def get(self, request):
        pincode = request.query_params.get("pincode")
        if not pincode:
            return HttpResponse.BadRequest("pincode is required")

        # Step 1: Get district from PincodeMaster
        try:
            pincode_record = PincodeMaster.objects.get(pincode=pincode)
        except PincodeMaster.DoesNotExist:
            return HttpResponse.BadRequest("Pincode not found")

        district = pincode_record.district
        if not district:
            return HttpResponse.BadRequest("District not found for this pincode")

        bank_name = request.query_params.get("bank_name")

        if bank_name:
            # Step 2: Get branches for district + bank_name
            qs = BankBranch.objects.filter(
                district__iexact=district.strip(),
                bank_name__iexact=bank_name.strip()
            ).order_by("branch_name")
            serializer = BankBranchSerializer(qs, many=True)
            return HttpResponse.Success({
                "district": district,
                "bank_name": bank_name,
                "count": qs.count(),
                "branches": serializer.data,
            })
        else:
            # Step 1 alternative: Get unique banks for this district
            bank_names = (
                BankBranch.objects.exclude(bank_name__isnull=True)
                .exclude(bank_name__exact="")
                .filter(district__iexact=district.strip())
                .values_list("bank_name", flat=True)
                .distinct()
                .order_by("bank_name")
            )
            return HttpResponse.Success({
                "district": district,
                "banks": list(bank_names),
                "count": len(bank_names),
            })


class ThirdPartyLenderListCreateView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="List third party lenders",
        description="Fetch a list of all third party lenders. Supports optional filtering by bank name.",
        parameters=[
            OpenApiParameter("bank_name", OpenApiTypes.STR, description="Filter by bank name"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        qs = ThirdPartyLender.objects.all()
        bank_name = request.query_params.get("bank_name")
        if bank_name:
            qs = qs.filter(bank_name__icontains=bank_name.strip())

        qs = qs.order_by("bank_name")
        serializer = ThirdPartyLenderSerializer(qs, many=True)
        return HttpResponse.Success({"count": qs.count(), "results": serializer.data})

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Create third party lender",
        description="Create a new third party lender record.",
        request=ThirdPartyLenderSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        serializer = ThirdPartyLenderSerializer(data=request.data)
        if serializer.is_valid():
            lender = serializer.save()
            return HttpResponse.Success({"third_party_lender": ThirdPartyLenderSerializer(lender).data})
        return HttpResponse.BadRequest(serializer.errors)


class ThirdPartyLenderDetailView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Update third party lender",
        description="Update an existing third party lender's details.",
        request=ThirdPartyLenderSerializer,
        responses={200: OpenApiTypes.OBJECT},
    )
    def patch(self, request, lender_id):
        try:
            lender = ThirdPartyLender.objects.get(id=lender_id)
            serializer = ThirdPartyLenderSerializer(lender, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"third_party_lender": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except ThirdPartyLender.DoesNotExist:
            return HttpResponse.BadRequest("Third party lender not found")

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Delete third party lender",
        description="Permanently delete a third party lender by their ID.",
        responses={200: OpenApiTypes.OBJECT},
    )
    def delete(self, request, lender_id):
        try:
            lender = ThirdPartyLender.objects.get(id=lender_id)
            lender.delete()
            return HttpResponse.Success({"message": "Third party lender deleted"})
        except ThirdPartyLender.DoesNotExist:
            return HttpResponse.BadRequest("Third party lender not found")


class CustomerBankAccountListView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="List customer bank accounts",
        description="Fetch a list of all customer bank accounts. Supports optional filtering by bank name.",
        parameters=[
            OpenApiParameter("bank_name", OpenApiTypes.STR, description="Filter by bank name"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        qs = CustomerBankAccount.objects.all()
        bank_name = request.query_params.get("bank_name")
        if bank_name:
            qs = qs.filter(bank_name__icontains=bank_name.strip())
        log.info("bank name : %s", str(qs))
        qs = qs.order_by("bank_name")
        serializer = CustomerBankAccountSerializer(qs, many=True)
        log.info("search result : %s", str(serializer.data))

        return HttpResponse.Success({"count": qs.count(), "results": serializer.data})


class DailyGoldRateListCreateView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="List daily gold rates",
        description="Fetch a list of daily gold rates. Supports filtering by product type, carat, and bank.",
        parameters=[
            OpenApiParameter("product_type", OpenApiTypes.STR, description="Filter by product type"),
            OpenApiParameter("carat", OpenApiTypes.STR, description="Filter by carat (e.g. 24K, 22K)"),
            OpenApiParameter("bank", OpenApiTypes.STR, description="Filter by bank (e.g. AXIS_BANK)"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        qs = DailyGoldRate.objects.all()
        product_type = request.query_params.get("product_type")
        if product_type:
            qs = qs.filter(product_type__iexact=product_type.strip())
        carat = request.query_params.get("carat")
        if carat:
            qs = qs.filter(carat__iexact=carat.strip())
        bank = request.query_params.get("bank")
        if bank:
            qs = qs.filter(bank__iexact=bank.strip())

        paginator = PageNumberPagination()
        paginator.page_size = 50
        paginator.page_size_query_param = "page_size"
        paginator.max_page_size = 200
        page = paginator.paginate_queryset(qs, request)
        serializer = DailyGoldRateSerializer(page, many=True)
        return HttpResponse.Success(
            {
                "count": qs.count(),
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data,
            }
        )

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Create daily gold rate",
        description="Create one or multiple daily gold rate records. Pass a single JSON object or a list for bulk creation.",
        request=DailyGoldRateSerializer,
        examples=[
            OpenApiExample(
                "Create single gold rate",
                value={
                    "product_type": "GENERAL_PURPOSE",
                    "carat": "24K",
                    "gold_rate": 7250.00,
                    "bank": "AXIS_BANK",
                },
                request_only=True,
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        if isinstance(request.data, list):
            serializer = DailyGoldRateSerializer(data=request.data, many=True)
            if serializer.is_valid():
                rates = serializer.save()
                return HttpResponse.Success(
                    {
                        "message": f"Successfully created {len(rates)} daily gold rates",
                        "count": len(rates),
                        "results": DailyGoldRateSerializer(rates, many=True).data,
                    }
                )
            return HttpResponse.BadRequest(serializer.errors)

        serializer = DailyGoldRateSerializer(data=request.data)
        if serializer.is_valid():
            rate = serializer.save()
            return HttpResponse.Success({"daily_gold_rate": DailyGoldRateSerializer(rate).data})
        return HttpResponse.BadRequest(serializer.errors)


class DailyGoldRateAuditHistoryView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Get gold rate audit history",
        description="Return a chronological audit log of daily gold rate create, update, and delete activities. Supports query param: 'id' (daily gold rate UUID).",
        parameters=[
            OpenApiParameter("days", OpenApiTypes.INT, description="Lookback period in days (default: 15)"),
            OpenApiParameter("carat", OpenApiTypes.STR, description="Filter by carat"),
            OpenApiParameter("bank", OpenApiTypes.STR, description="Filter by bank"),
            OpenApiParameter("id", OpenApiTypes.UUID, description="Filter by daily gold rate ID (UUID)"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        HistoricalDailyGoldRate = apps.get_model("onboarding_v2", "HistoricalDailyGoldRate")
        rate_id = request.query_params.get("id")
        
        qs = HistoricalDailyGoldRate.objects.all()
        if rate_id:
            qs = qs.filter(id=rate_id)
        else:
            now = timezone.now()
            date_from_param = request.query_params.get("date_from")
            date_to_param = request.query_params.get("date_to")
            days_param = request.query_params.get("days")

            from django.utils.dateparse import parse_date
            import datetime

            date_from_dt = None
            date_to_dt = None

            if date_from_param:
                parsed = parse_date(date_from_param)
                if parsed:
                    date_from_dt = timezone.make_aware(datetime.datetime.combine(parsed, datetime.time.min))

            if date_to_param:
                parsed = parse_date(date_to_param)
                if parsed:
                    date_to_dt = timezone.make_aware(datetime.datetime.combine(parsed, datetime.time.max))

            if not (date_from_dt or date_to_dt):
                try:
                    days = int(days_param) if days_param is not None else 3
                except (TypeError, ValueError):
                    days = 3
                date_from_dt = now - timedelta(days=days)
                date_to_dt = now
            
            if date_from_dt:
                qs = qs.filter(history_date__gte=date_from_dt)
            if date_to_dt:
                qs = qs.filter(history_date__lte=date_to_dt)

        qs = qs.order_by("-history_date")

        carat = request.query_params.get("carat")
        if carat:
            qs = qs.filter(carat__iexact=carat.strip())
        bank = request.query_params.get("bank")
        if bank:
            qs = qs.filter(bank__iexact=bank.strip())

        paginator = PageNumberPagination()
        paginator.page_size = 50
        paginator.page_size_query_param = "page_size"
        paginator.max_page_size = 200
        page = paginator.paginate_queryset(qs, request)

        results = []
        for entry in page:
            history_user = getattr(entry, "history_user", None)
            user_name = None
            user_id = None
            if history_user:
                user_name = " ".join(filter(None, [getattr(history_user, "first_name", None), getattr(history_user, "last_name", None)])) or getattr(history_user, "username", None) or getattr(history_user, "phone", None)
                user_id = getattr(history_user, "user_id", None) or getattr(history_user, "pk", None)

            action_type = {
                "+": "CREATE",
                "~": "UPDATE",
                "-": "DELETE",
            }.get(entry.history_type, entry.history_type or "UNKNOWN")

            previous_value = None
            new_value = None
            details = []

            if entry.history_type == "~" and entry.prev_record is not None:
                diff = entry.diff_against(entry.prev_record)
                details = [
                    {
                        "field": change.field,
                        "previous_value": change.old,
                        "new_value": change.new,
                    }
                    for change in diff.changes
                ]
                previous_value = {change.field: change.old for change in diff.changes}
                new_value = {change.field: change.new for change in diff.changes}
            elif entry.history_type == "+":
                details = [{"field": field, "new_value": value} for field, value in entry.__dict__.items() if field in {"product_type", "carat", "bank", "gold_rate", "metadata"}]
                new_value = {field: value for field, value in entry.__dict__.items() if field in {"product_type", "carat", "bank", "gold_rate", "metadata"}}
            elif entry.history_type == "-":
                previous_value = {field: value for field, value in entry.__dict__.items() if field in {"product_type", "carat", "bank", "gold_rate", "metadata"}}
                details = [{"field": field, "previous_value": value} for field, value in previous_value.items()]

            results.append(
                {
                    "id": str(entry.id),
                    "history_id": str(entry.history_id),
                    "action_type": action_type,
                    "user_name": user_name,
                    "user_id": str(user_id) if user_id else None,
                    "action_timestamp": entry.history_date.isoformat() if getattr(entry, "history_date", None) else None,
                    "gold_rate_id": str(entry.id),
                    "product_type": entry.product_type,
                    "carat": entry.carat,
                    "bank": entry.bank,
                    "previous_value": previous_value,
                    "new_value": new_value,
                    "details": details,
                }
            )

        return HttpResponse.Success(
            {
                "count": qs.count(),
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": results,
            }
        )


class DailyGoldRateDetailView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Update daily gold rate",
        description="Update an existing daily gold rate. Only the fields provided will be updated (partial update).",
        request=DailyGoldRateSerializer,
        examples=[
            OpenApiExample(
                "Update rate",
                value={
                    "gold_rate": 7300.00,
                    "bank": "AXIS_BANK",
                },
                request_only=True,
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def patch(self, request, rate_id):
        try:
            rate = DailyGoldRate.objects.get(id=rate_id)
            serializer = DailyGoldRateSerializer(rate, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"daily_gold_rate": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except DailyGoldRate.DoesNotExist:
            return HttpResponse.BadRequest("Daily gold rate not found")


    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Delete daily gold rate",
        description="Permanently delete a daily gold rate record by its ID.",
        responses={200: OpenApiTypes.OBJECT},
    )
    def delete(self, request, rate_id):
        try:
            rate = DailyGoldRate.objects.get(id=rate_id)
            rate.delete()
            return HttpResponse.Success({"message": "Daily gold rate deleted"})
        except DailyGoldRate.DoesNotExist:
            return HttpResponse.BadRequest("Daily gold rate not found")


class RoiConfigurationListCreateView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="List ROI configurations",
        description="Fetch a list of ROI configurations. Supports filtering by lead type, bank, product type, tenure, and repayment schedule.",
        parameters=[
            OpenApiParameter("lead_type", OpenApiTypes.STR, description="Filter by lead type"),
            OpenApiParameter("bank", OpenApiTypes.STR, description="Filter by bank"),
            OpenApiParameter("product_type", OpenApiTypes.STR, description="Filter by product type"),
            OpenApiParameter("tenure", OpenApiTypes.STR, description="Filter by tenure"),
            OpenApiParameter("repayment_schedule", OpenApiTypes.STR, description="Filter by repayment schedule"),
            OpenApiParameter("loan_range", OpenApiTypes.STR, description="Filter by loan range"),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        qs = RoiConfiguration.objects.all()
        lead_type = request.query_params.get("lead_type")
        if lead_type:
            qs = qs.filter(lead_type__iexact=lead_type.strip())
        bank = request.query_params.get("bank")
        if bank:
            qs = qs.filter(bank__iexact=bank.strip())
        product_type = request.query_params.get("product_type")
        if product_type:
            qs = qs.filter(product_type__iexact=product_type.strip())
        tenure = request.query_params.get("tenure")
        if tenure:
            qs = qs.filter(tenure__iexact=tenure.strip())
        repayment_schedule = request.query_params.get("repayment_schedule")
        if repayment_schedule:
            qs = qs.filter(repayment_schedule__iexact=repayment_schedule.strip())
        loan_range = request.query_params.get("loan_range")
        if loan_range:
            qs = qs.filter(loan_range__iexact=loan_range.strip())

        paginator = PageNumberPagination()
        paginator.page_size = 50
        paginator.page_size_query_param = "page_size"
        paginator.max_page_size = 200
        page = paginator.paginate_queryset(qs, request)
        serializer = RoiConfigurationSerializer(page, many=True)
        return HttpResponse.Success(
            {
                "count": qs.count(),
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data,
            }
        )

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Create ROI configuration",
        description="Create one or multiple ROI configuration records. Pass a single JSON object or a list for bulk creation.",
        request=RoiConfigurationSerializer,
        examples=[
            OpenApiExample(
                "Create single ROI configuration",
                value={
                    "lead_type": "CO_LENDING",
                    "bank": "AXIS_BANK",
                    "product_type": "GENERAL_PURPOSE",
                    "tenure": "6_MONTHS",
                    "repayment_schedule": "BULLET",
                    "loan_range": "LESS_THAN_2_5_LAKHS",
                    "bank_roi": 15.00,
                    "manipal_roi": 25.00,
                },
                request_only=True,
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        if isinstance(request.data, list):
            serializer = RoiConfigurationSerializer(data=request.data, many=True)
            if serializer.is_valid():
                configs = serializer.save()
                return HttpResponse.Success(
                    {
                        "message": f"Successfully created {len(configs)} ROI configurations",
                        "count": len(configs),
                        "results": RoiConfigurationSerializer(configs, many=True).data,
                    }
                )
            return HttpResponse.BadRequest(serializer.errors)

        serializer = RoiConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            config = serializer.save()
            return HttpResponse.Success({"roi_configuration": RoiConfigurationSerializer(config).data})
        return HttpResponse.BadRequest(serializer.errors)


class RoiConfigurationDetailView(APIView):
    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Update ROI configuration",
        description="Update an existing ROI configuration. Only the fields provided will be updated (partial update).",
        request=RoiConfigurationSerializer,
        examples=[
            OpenApiExample(
                "Update ROI values",
                value={
                    "bank_roi": 16.00,
                    "manipal_roi": 26.00,
                },
                request_only=True,
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    def patch(self, request, config_id):
        try:
            config = RoiConfiguration.objects.get(id=config_id)
            serializer = RoiConfigurationSerializer(config, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"roi_configuration": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except RoiConfiguration.DoesNotExist:
            return HttpResponse.BadRequest("ROI configuration not found")

    @extend_schema(
        tags=["Onboarding V2 Admin"],
        summary="Delete ROI configuration",
        description="Permanently delete an ROI configuration record by its ID.",
        responses={200: OpenApiTypes.OBJECT},
    )
    def delete(self, request, config_id):
        try:
            config = RoiConfiguration.objects.get(id=config_id)
            config.delete()
            return HttpResponse.Success({"message": "ROI configuration deleted"})
        except RoiConfiguration.DoesNotExist:
            return HttpResponse.BadRequest("ROI configuration not found")
