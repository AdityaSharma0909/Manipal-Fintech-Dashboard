import traceback
import pandas as pd
from io import BytesIO as IO # for modern python
from django.http import HttpResponse as dhttp
from rest_framework.views import APIView
from django.db.models import Q
from utils.constants import ROLES
from utils.responseHandler import HttpResponse
from onboarding_v2.helpers.lead_application_helpers import filter_leads
from onboarding_v2.serializers import LeadCreateSerializer
from onboarding_v2.models import PincodeMaster
from users.models import User
from django.utils import timezone
from datetime import datetime
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse

class ExportLeadView(APIView):
    
    @extend_schema(
        summary="Export Leads Data",
        description="Export the filtered leads data as an Excel file. Uses the same filters as the Leads List API.",
        parameters=[
            OpenApiParameter(name='district', description='Filter by District (comma-separated)', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='state', description='Filter by State (comma-separated)', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='creation_start_date', description='Creation start date (YYYY-MM-DD)', required=False, type=OpenApiTypes.DATE),
            OpenApiParameter(name='creation_end_date', description='Creation end date (YYYY-MM-DD)', required=False, type=OpenApiTypes.DATE),
            OpenApiParameter(name='created_on', description='Exact creation date (YYYY-MM-DD)', required=False, type=OpenApiTypes.DATE),
            OpenApiParameter(name='status', description='Filter by Status (comma-separated)', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='product_subcategory', description='Filter by Product Subcategory (comma-separated)', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='source', description='Filter by Source', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='punched_by', description='Filter by Agent Employee ID', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='manager_id', description='Filter by Manager ID (UUID or Employee ID)', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='doj_start_date', description='Agent Date of Joining start date (YYYY-MM-DD)', required=False, type=OpenApiTypes.DATE),
            OpenApiParameter(name='doj_end_date', description='Agent Date of Joining end date (YYYY-MM-DD)', required=False, type=OpenApiTypes.DATE),
        ],
        responses={
            200: OpenApiResponse(response=OpenApiTypes.BINARY, description='Excel file containing leads'),
            403: OpenApiResponse(response=OpenApiTypes.OBJECT, description='Forbidden'),
            500: OpenApiResponse(response=OpenApiTypes.OBJECT, description='Internal Server Error'),
        }
    )
    def get(self, request):
        try:
            
            user = request.user
            if user.role == ROLES.LOAN_OFFICER.value:
                return HttpResponse.Forbidden("Not Allowed")

            qs = filter_leads(request.user, request.query_params, all_users=True).prefetch_related("applications")

            # Scope export results for Tele roles
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

            from onboarding_v2.helpers.lead_export_helpers import generate_leads_excel

            excel_file = generate_leads_excel(qs)
            if not excel_file:
                return HttpResponse.BadRequest("Leads not found")

            response = dhttp(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            response['Content-Disposition'] = 'attachment; filename=Leads_Data.xlsx'
            return response

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
