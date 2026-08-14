import datetime
import traceback
import pandas as pd
import csv
from io import BytesIO as IO, StringIO
from django.http import HttpResponse as dhttp
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from utils.constants import ROLES
from utils.responseHandler import HttpResponse
from users.service.export_user_data import ExportUserService
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse


class ExportUserView(APIView):
    """
    API endpoint for exporting user data as Excel only.

    Query Parameters:
    - include_customers: '0' or '1' (default: '0')
    - start_date: ISO date (YYYY-MM-DD) to filter `date_of_joining` from (inclusive)
    - end_date: ISO date (YYYY-MM-DD) to filter `date_of_joining` to (inclusive)
    """

    @extend_schema(
        summary="Export Users",
        description=(
            "Export the user list as an Excel file. Requires authentication via Bearer token. "
            "Query params `include_customers`, `doj_start_date`, `doj_end_date`, `creation_start_date`, and `creation_end_date` control results."
        ),
        parameters=[
            OpenApiParameter(
                name='include_customers',
                description="Include users with role CUSTOMER. Use '1' or '0'.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='doj_start_date',
                description='Filter date_of_joining from this date (YYYY-MM-DD)',
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='doj_end_date',
                description='Filter date_of_joining until this date (YYYY-MM-DD)',
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='creation_start_date',
                description='Filter date_joined from this date (YYYY-MM-DD)',
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='creation_end_date',
                description='Filter date_joined until this date (YYYY-MM-DD)',
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='state',
                description='Filter by state (comma-separated for multiple)',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='district',
                description='Filter by district (comma-separated for multiple)',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='role',
                description='Filter by Role (comma-separated)',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='status',
                description='Filter by Status (Active or Inactive)',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='designation',
                description='Filter by Designation (comma-separated)',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='team',
                description='Filter by Team (comma-separated)',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: OpenApiResponse(response=OpenApiTypes.BINARY, description='Excel file'),
            400: OpenApiResponse(response=OpenApiTypes.OBJECT, description='Bad request'),
            401: OpenApiResponse(response=OpenApiTypes.OBJECT, description='Unauthorized'),
        },
    )
    def get(self, request):
        try:
            user = request.user
            # Allow all authenticated users to download the export
            if not getattr(user, "is_authenticated", False):
                return HttpResponse.Forbidden("Authentication required")
            
            # Get query parameters
            include_customers = request.query_params.get('include_customers', '0') == '1'

            # Optional date filters
            doj_start_date = request.query_params.get('doj_start_date') or request.query_params.get('start_date')
            doj_end_date = request.query_params.get('doj_end_date') or request.query_params.get('end_date')
            creation_start_date = request.query_params.get('creation_start_date')
            creation_end_date = request.query_params.get('creation_end_date')
            
            # Optional location filters
            state = request.query_params.get('state')
            district = request.query_params.get('district')
            
            # Additional optional filters
            role = request.query_params.get('role')
            status = request.query_params.get('status')
            designation = request.query_params.get('designation')
            team = request.query_params.get('team')

            # Validate date format (if provided)
            for dname, dval in (('doj_start_date', doj_start_date), ('doj_end_date', doj_end_date), ('creation_start_date', creation_start_date), ('creation_end_date', creation_end_date)):
                if dval:
                    try:
                        datetime.datetime.strptime(dval, '%Y-%m-%d')
                    except Exception:
                        return HttpResponse.BadRequest({"message": f"Invalid {dname} format. Use YYYY-MM-DD"})

            output = ExportUserService().exportUser(
                request, 
                include_customers=include_customers, 
                doj_start_date=doj_start_date, 
                doj_end_date=doj_end_date,
                creation_start_date=creation_start_date,
                creation_end_date=creation_end_date,
                state=state,
                district=district,
                role=role,
                status=status,
                designation=designation,
                team=team
            )
            if not output:
                return HttpResponse.BadRequest({"message": "No User found"})
            
            columns = ['username','first_name','last_name','phone','role','designation','aadhar_no','pan_no','employee_id','employee_profile_photo','date_of_joining','email','entity_id','state','district']
            df_output = pd.DataFrame(output, columns=columns)
            
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            
            # Always return Excel
            return self._export_excel(df_output, current_date)

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
    
    def _export_csv(self, df, current_date):
        """Export data as CSV"""
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, quoting=csv.QUOTE_ALL)
        
        response = dhttp(csv_buffer.getvalue(), content_type='text/csv; charset=utf-8')
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        response['Content-Disposition'] = f'attachment; filename=User_Report_{current_date}.csv'
        return response
    
    def _export_excel(self, df, current_date):
        """Export data as Excel"""
        excel_file = IO()
        xlwriter = pd.ExcelWriter(excel_file, engine='openpyxl')
        df.to_excel(xlwriter, 'Users Report', index=False)
        xlwriter.close()
        excel_file.seek(0)
        
        response = dhttp(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        response['Content-Disposition'] = f'attachment; filename=User_Report_{current_date}.xlsx'
        return response