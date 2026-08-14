from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from users.service.userService import UserService
from utility.api_framework import ApiFramework
from utility.response_handler import HttpResponse as ApiHttpResponse
from utils.constants import ROLES


class EmployeePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 1000

from datetime import datetime

class AllEmployeeUtils(ApiFramework):

    def __init__(self, data, method, **kwargs):
        super().__init__()
        self.__data=data
        self.__method=method
        self.__response={}
        self.__pagination=kwargs.get('pagination')
        self.__request=kwargs.get('request')


    def run_logic(self):
        service=UserService()
        if self.__method=='GET':
            self.__response=service.get_users(request=self.__request,
                                              pagination=self.__pagination,
                                              **self.__data
                                              )
        elif self.__method=='PATCH':
            self.__response=service.update_user(
                user_id=self.__data.get('user_id'),
                data=self.__data,
                actor_role=getattr(self.__request.user, 'role', None) if self.__request else None
            )
        elif self.__method=='APPLICATION_GET':
            self.__response=service.get_all_application_per_user(**self.__data)
        elif self.__method=='POST':
            self.__response=service.create_user(
                data=self.__data,
                actor_role=getattr(self.__request.user, 'role', None) if self.__request else None
            )
        elif self.__method == "DELETE":
           self.__response = service.delete_user(
               user_id=self.__data.get("user_id"),
               actor_role=self.__data.get("actor_role"),
           )

    def process(self):
        return self.__response

class AllEmployeeView(APIView, PageNumberPagination):
    permission_classes = []

    @extend_schema(
        summary="List employees",
        description=(
            "Returns the employee list with optional filters and free-text search. "
            "When `role__in` is not provided, users with CUSTOMER, SUPER_ADMIN, and CPC roles "
            "are excluded by default."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Free-text search across `first_name`, `last_name`, `employee_id`, "
                    "`phone`, `district`, and `username`. Example: `rahul` or `10023`."
                ),
            ),
            OpenApiParameter(name="user_id", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filter by user ID. Example: `550e8400-e29b-41d4-a716-446655440000`"),
            OpenApiParameter(name="first_name", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filter by first name. Example: `Rahul`"),
            OpenApiParameter(name="last_name", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filter by last name. Example: `Sharma`"),
            OpenApiParameter(name="phone", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filter by phone number. Example: `9876543210`"),
            OpenApiParameter(
                name="role__in",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated role names. Example: `AGENT,SALES_OFFICER`.",
            ),
            OpenApiParameter(name="aadhar_no", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filter by Aadhaar number. Example: `123456789012`"),
            OpenApiParameter(name="employee_id", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filter by employee ID. Example: `EMP1001`"),
            OpenApiParameter(name="is_active", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, description="Filter by active status. Example: `true`"),
            OpenApiParameter(name="email", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filter by email address. Example: `rahul@example.com`"),
            OpenApiParameter(
                name="date_of_joining",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by exact date of joining (YYYY-MM-DD). Example: `2023-01-15`.",
            ),
            OpenApiParameter(
                name="date_of_joining__gte",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter joined on or after date (YYYY-MM-DD). Example: `2023-01-01`.",
            ),
            OpenApiParameter(
                name="date_of_joining__lte",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter joined on or before date (YYYY-MM-DD). Example: `2023-12-31`.",
            ),
            OpenApiParameter(
                name="lm_branch_map__branch__branch_code",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by branch code. Example: `BR001`.",
            ),
            OpenApiParameter(name="team", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filter by team."),
            OpenApiParameter(name="district", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, description="Filter by district."),
            OpenApiParameter(
                name="district__in",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated districts. Example: `Pune,Mumbai`.",
            ),
            OpenApiParameter(
                name="branch",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Comma-separated branch IDs. Example: `uuid1,uuid2`.",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for paginated results.",
            ),
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of results to return per page.",
            ),
        ],
    )
    def get(self, request):
        filters = dict(request.GET)
        data = {'role': request.user.role, 'filters': filters}

        # If user is not SUPER_ADMIN or CPC, then filter by branch
        # if request.user.role not in [ROLES.SUPER_ADMIN.value, ROLES.CPC.value, ROLES.CENTRAL_OPS.value]:
        #     branch = request.user.lm_branch_map.all().first()
        #     if branch is not None:
        #         data['branch'] = branch.branch_id

        return AllEmployeeUtils(data=data, method='GET', pagination=EmployeePagination, request=request).main()



    def patch(self, request):
        data=request.data
        return AllEmployeeUtils(data=data, method='PATCH', request=request).main()

    @extend_schema(
        summary="Create employee",
        description="Creates a new employee user.",
        request=inline_serializer(
            name="EmployeeCreateRequest",
            fields={
                "date_of_joining": serializers.DateField(required=False),
                "exclude_from_bt_date_logic": serializers.BooleanField(required=False, default=False),
                "employee_id": serializers.CharField(required=False, allow_blank=True, allow_null=True),
                "username": serializers.CharField(required=False, allow_blank=True, allow_null=True),
                "phone": serializers.CharField(required=True),
                "first_name": serializers.CharField(required=True),
                "last_name": serializers.CharField(required=False, allow_blank=True, allow_null=True),
                "role": serializers.CharField(required=True),
                "designation": serializers.CharField(required=False, allow_blank=True, allow_null=True),
                "team": serializers.CharField(required=False, allow_blank=True, allow_null=True),
                "email": serializers.EmailField(required=False, allow_blank=True, allow_null=True),
                "pincode": serializers.CharField(required=False, allow_blank=True, allow_null=True),
                "state": serializers.CharField(required=False, allow_blank=True, allow_null=True),
                "district": serializers.CharField(required=False, allow_blank=True, allow_null=True),
                "user_id": serializers.CharField(required=False, allow_null=True),
            },
        ),
        examples=[
            OpenApiExample(
                name="Sales Officer Create Payload",
                value={
                    "date_of_joining": "2026-04-14",
                    "exclude_from_bt_date_logic": False,
                    "employee_id": "SG009",
                    "username": "SG009",
                    "phone": "7001385745",
                    "first_name": "swati",
                    "last_name": "mondal",
                    "role": "SALES_OFFICER",
                    "designation": "FOS",
                    "team": "DST",
                    "email": "tiest@gmail.com",
                    "pincode": "743273",
                    "state": "WEST BENGAL",
                    "district": "24 PARAGANAS NORTH",
                    "user_id": None,
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        data=request.data
        service = UserService()
        actor_role = service.normalize_role(getattr(request.user, 'role', None))
        requested_role = service.normalize_role(data.get('role'))
        print(f"EMPLOYEE_CREATE actor_role={actor_role} requested_role={requested_role} user_class={request.user.__class__.__name__}")

        permission_error = service.validate_create_user_permission(actor_role, requested_role)
        if permission_error:
            return ApiHttpResponse().response(
                permission_error.get('status_code', 403),
                permission_error.get('data'),
                error_msg=permission_error.get('error_msg'),
                error_code=permission_error.get('error_code'),
            )

        return AllEmployeeUtils(data=data, method='POST', request=request).main()
    def delete(self, request):
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        if not data.get("user_id"):
            data["user_id"] = request.query_params.get("user_id")
        data["actor_role"] = getattr(request.user, "role", None)
        return AllEmployeeUtils(data=data, method="DELETE", request=request).main()


class ApplicationPerEmployee(APIView):

    def get(self, request):
        data={'user_id':request.GET.get('user_id'),
              'role':request.GET.get('role', None)}
        return AllEmployeeUtils(data=data, method='APPLICATION_GET').main()


class SalesOfficerBulkUploadView(APIView):
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Bulk upload Sales Officers",
        description=(
            "Upload an Excel file of Sales Officers. Each row is processed independently and "
            "only `SALES_OFFICER` users are created with fixed `designation=FOS` and `team=DST`."
        ),
        request=inline_serializer(
            name='SalesOfficerBulkUploadRequest',
            fields={
                'file': serializers.FileField(required=True),
                'date_of_joining': serializers.DateField(required=False),
            },
        ),
        responses={
            200: inline_serializer(
                name='SalesOfficerBulkUploadResponse',
                fields={
                    'status': serializers.CharField(),
                    'status_code': serializers.IntegerField(),
                    'data': inline_serializer(
                        name='SalesOfficerBulkUploadResponseData',
                        fields={
                            'total_rows': serializers.IntegerField(),
                            'created_count': serializers.IntegerField(),
                            'failed_count': serializers.IntegerField(),
                            'results': inline_serializer(
                                name='SalesOfficerBulkUploadRowResult',
                                fields={
                                    'row_number': serializers.IntegerField(),
                                    'ecode': serializers.CharField(allow_null=True, required=False),
                                    'status': serializers.CharField(),
                                    'user_id': serializers.CharField(allow_null=True, required=False),
                                    'error': serializers.CharField(allow_null=True, required=False),
                                },
                                many=True,
                            ),
                        },
                    ),
                },
            ),
            400: inline_serializer(
                name='SalesOfficerBulkUploadErrorResponse',
                fields={
                    'status': serializers.CharField(),
                    'status_code': serializers.IntegerField(),
                    'data': inline_serializer(
                        name='SalesOfficerBulkUploadErrorData',
                        fields={'msg': serializers.CharField()},
                    ),
                    'error_msg': inline_serializer(
                        name='SalesOfficerBulkUploadErrorMessage',
                        fields={'msg': serializers.CharField()},
                    ),
                    'error_code': serializers.IntegerField(),
                },
            ),
        },
    )
    def post(self, request):
        service = UserService()
        actor_role = service.normalize_role(getattr(request.user, 'role', None))
        permission_error = service.validate_create_user_permission(actor_role, ROLES.SALES_OFFICER.value)
        if permission_error:
            return ApiHttpResponse().response(
                permission_error.get('status_code', 403),
                permission_error.get('data'),
                error_msg=permission_error.get('error_msg'),
                error_code=permission_error.get('error_code'),
            )

        excel_file = request.FILES.get('file')
        if not excel_file:
            return ApiHttpResponse().response(
                400,
                {'msg': 'file is required'},
                error_msg={'msg': 'file is required'},
                error_code=400,
            )

        date_of_joining = request.data.get('date_of_joining')
        if date_of_joining:
            try:
                date_of_joining = datetime.strptime(date_of_joining, '%Y-%m-%d').date()
            except ValueError:
                return ApiHttpResponse().response(
                    400,
                    {'msg': 'date_of_joining must be in YYYY-MM-DD format'},
                    error_msg={'msg': 'date_of_joining must be in YYYY-MM-DD format'},
                    error_code=400,
                )

        response_data = service.create_sales_officers_from_excel(
            excel_file=excel_file,
            actor_role=actor_role,
            date_of_joining=date_of_joining,
        )
        return ApiHttpResponse().response(
            response_data.get('status_code', 200),
            response_data.get('data'),
            error_msg=response_data.get('error_msg'),
            error_code=response_data.get('error_code'),
        )
