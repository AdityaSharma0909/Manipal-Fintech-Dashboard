from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from users.models import User, TimeStamp
from utils.constants import TIMESTAMP
from collections import defaultdict
from datetime import timedelta
import calendar
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    tags=["Reports"],
    summary="User Report",
    description=(
        "Returns aggregated user counts grouped by **Role**, **Team**, and **Designation**. "
        "Supports optional filtering by `state`, `district`, and `is_active` status. "
        "The response is structured to be directly consumable by frontend charting libraries "
        "(e.g. Chart.js, Recharts, Highcharts)."
    ),
    parameters=[
        OpenApiParameter(
            name="state",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter users by state (case-insensitive). Example: `Karnataka`",
        ),
        OpenApiParameter(
            name="district",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter users by district (case-insensitive). Example: `Bengaluru`",
        ),
        OpenApiParameter(
            name="is_active",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter users by active status. Pass `true` or `false`.",
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="Aggregated user report data grouped by role, team, and designation.",
            examples=[
                OpenApiExample(
                    name="Successful Response",
                    value={
                        "filters_applied": {
                            "state": "Karnataka",
                            "district": "Bengaluru",
                            "is_active": "true"
                        },
                        "reports": {
                            "by_role": [
                                {"role": "SUPER_ADMIN", "count": 3},
                                {"role": "SALES_OFFICER", "count": 3},
                                {"role": "AGENT", "count": 1},
                            ],
                            "by_team": [
                                {"team": "Sales", "count": 4},
                                {"team": "Operations", "count": 2},
                            ],
                            "by_designation": [
                                {"designation": "Manager", "count": 2},
                                {"designation": "Executive", "count": 5},
                            ]
                        }
                    },
                    response_only=True,
                )
            ],
        )
    },
)
class UserReportAPIView(APIView):
    """
    API View to return aggregated user data for reporting.
    Groups users by role, team, and designation.
    Supports filtering by state, district, and is_active.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        queryset = User.objects.all()

        # Apply filters from query params
        state = request.GET.get('state')
        district = request.GET.get('district')

        if state:
            queryset = queryset.filter(state__iexact=state)
        if district:
            queryset = queryset.filter(district__iexact=district)

        is_active = request.GET.get('is_active')
        if is_active is not None:
            # Handle string boolean values
            is_active_bool = str(is_active).lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)

        # Aggregate counts
        roles_data = queryset.values('role').annotate(count=Count('user_id')).order_by('-count')
        teams_data = queryset.values('team').annotate(count=Count('user_id')).order_by('-count')
        designations_data = queryset.values('designation').annotate(count=Count('user_id')).order_by('-count')

        # Structure response for graphical plotting
        response_data = {
            'filters_applied': {
                'state': state,
                'district': district,
                'is_active': is_active
            },
            'reports': {
                'by_role': list(roles_data),
                'by_team': list(teams_data),
                'by_designation': list(designations_data)
            }
        }

        return Response(response_data)


@extend_schema(
    tags=["Reports"],
    summary="Attendance Report",
    description=(
        "Returns aggregated day-wise, week-wise, and month-wise counts of unique users who logged in (checked in). "
        "Supports optional filtering by `start_date`, `end_date`, `role`, `team`, and `designation`."
    ),
    parameters=[
        OpenApiParameter(
            name="start_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Start date for filtering (YYYY-MM-DD).",
        ),
        OpenApiParameter(
            name="end_date",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="End date for filtering (YYYY-MM-DD).",
        ),
        OpenApiParameter(
            name="role",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter by user role.",
        ),
        OpenApiParameter(
            name="team",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter by user team.",
        ),
        OpenApiParameter(
            name="designation",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter by user designation.",
        ),
    ],
    responses={
        200: {
            "description": "Aggregated attendance report data.",
        }
    },
)
class AttendanceReportAPIView(APIView):
    """
    API View to return aggregated attendance data for reporting.
    Groups check-ins by day, week, and month.
    """
    permission_classes = [AllowAny]

    def get_aggregated_data(self, queryset, truncate_func, date_field_name, format_func=None):
        qs = queryset.annotate(**{date_field_name: truncate_func('created_at')}).select_related('user').order_by(date_field_name)
        agg_dict = defaultdict(lambda: {'count': 0, 'users': {}})
        
        for record in qs:
            date_val = getattr(record, date_field_name)
            if not date_val:
                continue

            if format_func:
                display_date = format_func(date_val)
            else:
                display_date = str(date_val.date()) if hasattr(date_val, 'date') else str(date_val)

            user = record.user
            if user and user.user_id not in agg_dict[display_date]['users']:
                agg_dict[display_date]['users'][user.user_id] = {
                    'user_id': str(user.user_id),
                    'name': f"{user.first_name} {user.last_name}".strip(),
                    'phone': str(user.phone) if user.phone else None,
                    'employee_id': user.employee_id,
                    'role': user.role,
                    'designation': user.designation,
                }
                agg_dict[display_date]['count'] += 1

        return [
            {
                date_field_name: date_val,
                'count': data['count'],
                'users': list(data['users'].values())
            }
            for date_val, data in agg_dict.items()
        ]

    def get(self, request, *args, **kwargs):
        # Base queryset: only CHECKED_IN records
        queryset = TimeStamp.objects.filter(status=TIMESTAMP.CHECKED_IN.value)

        # Apply filters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        role = request.GET.get('role')
        team = request.GET.get('team')
        designation = request.GET.get('designation')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        if role:
            queryset = queryset.filter(user__role__iexact=role)
        if team:
            queryset = queryset.filter(user__team__iexact=team)
        if designation:
            queryset = queryset.filter(user__designation__iexact=designation)

        # Annotate and aggregate with details
        day_wise = self.get_aggregated_data(
            queryset, TruncDate, 'date',
            format_func=lambda d: d.strftime('%Y-%m-%d')
        )
        week_wise = self.get_aggregated_data(
            queryset, TruncWeek, 'week',
            format_func=lambda d: f"{d.strftime('%Y-%m-%d')} to {(d + timedelta(days=6)).strftime('%Y-%m-%d')}"
        )
        month_wise = self.get_aggregated_data(
            queryset, TruncMonth, 'month',
            format_func=lambda d: f"{d.strftime('%Y-%m-01')} to {d.strftime('%Y-%m')}-{calendar.monthrange(d.year, d.month)[1]:02d}"
        )

        # Structure response
        response_data = {
            'filters_applied': {
                'start_date': start_date,
                'end_date': end_date,
                'role': role,
                'team': team,
                'designation': designation
            },
            'reports': {
                'day_wise': day_wise,
                'week_wise': week_wise,
                'month_wise': month_wise
            }
        }

        return Response(response_data)
