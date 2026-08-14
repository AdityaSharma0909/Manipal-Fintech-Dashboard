from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from tasks.models import SubTask
from users.models import User, UserReward, TimeStamp
from users.serializers import UserResponseSerializer
# from disbursements.models import Disbursement
from utils.constants import SUBTASK_STATUS, ROLES, SALES_PAYOUT_TYPE, TASK_STATUS
from payment.models import SalesOfficerPayout
from onboarding_v2.helpers.lead_application_helpers import filter_leads, filter_applications
from onboarding_v2.models import LeadV2, ApplicationV2
from onboarding_v2.constants import LeadType, ApplicationStatus


class TaskEarningsView(APIView):
    permission_classes = []

    def get(self, request):
        user = request.user
        today = timezone.localtime().date()
        rewards = UserReward.objects.filter(user=user)
        rewards_total = rewards.aggregate(total=Sum("amount"))["total"] or 0
        rewards_today = (
            rewards.filter(created_at__date=today).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        incentive_total = 0
        incentive_today = 0
        incentive_items = []
        if user.role == ROLES.SALES_OFFICER.value:
            payouts = SalesOfficerPayout.objects.filter(
                so_user=user, payout_type=SALES_PAYOUT_TYPE.INCENTIVE.value
            ).order_by("-created_at")
            incentive_total = payouts.aggregate(total=Sum("amount"))["total"] or 0
            incentive_today = (
                payouts.filter(created_at__date=today).aggregate(total=Sum("amount"))["total"]
                or 0
            )
            for p in payouts[:200]:
                incentive_items.append(
                    {
                        "date": p.created_at.date().isoformat() if getattr(p, "created_at", None) else None,
                        "amount": float(p.amount),
                        "type": "Incentive",
                        "customer_id": p.customer_id,
                        "customer_name": p.customer_name,
                        # "agent_name": p.agent_name,
                        "status": p.status,
                    }
                )
        reward_items = []
        for r in rewards.order_by("-created_at")[:200]:
            reward_items.append(
                {
                    "date": r.created_at.date().isoformat(),
                    "amount": float(r.amount),
                    "type": "Reward",
                    "description": r.description or "",
                }
            )
        items = sorted(incentive_items + reward_items, key=lambda x: x.get("date") or "", reverse=True)
        total_earning = (rewards_total or 0) + (incentive_total or 0)
        today_earning = (rewards_today or 0) + (incentive_today or 0)
        payload = {
            "earnings": {
                "today_earning": float(today_earning),
                "total_earning": float(total_earning),
                "period": f"Till {today.strftime('%d %b %y')}",
            },
            "items": items,
        }
        return Response({"status": "success", "data": payload}, status=status.HTTP_200_OK)


class TaskDisbursementView(APIView):
    permission_classes = []

    def get(self, request):
        user = request.user
        apps = (
            filter_applications(user, request.query_params)
            .filter(status=ApplicationStatus.APPROVED)
        )
        by_cat = (
            apps.values("lead__product_subcategory")
            .annotate(total=Sum("lead__amount"))
            .order_by("lead__product_subcategory")
        )
        breakdown = [
            {
                "name": row["lead__product_subcategory"] or "UNKNOWN",
                "amount": float(row["total"] or 0),
            }
            for row in by_cat
        ]
        total = sum(row["amount"] for row in breakdown)
        payload = {
            "disbursement": {
                "current": float(total),
                "target": 1000000,
            },
            "breakdown": breakdown,
        }
        return Response({"status": "success", "data": payload}, status=status.HTTP_200_OK)



class TaskDashboardHomeView(APIView):
    permission_classes = []

    def get(self, request):
        user = request.user
        today = timezone.localtime().date()

        # 1. USER PROFILE
        profile = {
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "city": user.city,
            "state": user.state,
        }
        
        # 2. EARNINGS
        rewards = UserReward.objects.filter(user=user)
        rewards_total = rewards.aggregate(total=Sum("amount"))["total"] or 0
        rewards_today = (
            rewards.filter(created_at__date=today).aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        incentive_total = 0
        incentive_today = 0
        if user.role == ROLES.SALES_OFFICER.value:
            payouts = SalesOfficerPayout.objects.filter(
                so_user=user, payout_type=SALES_PAYOUT_TYPE.INCENTIVE.value
            )
            incentive_total = payouts.aggregate(total=Sum("amount"))["total"] or 0
            incentive_today = (
                payouts.filter(created_at__date=today).aggregate(total=Sum("amount"))[
                    "total"
                ]
                or 0
            )

        total_earning = (rewards_total or 0) + (incentive_total or 0)
        today_earning = (rewards_today or 0) + (incentive_today or 0)

        earnings = {
            "today_earning": float(today_earning),
            "total_earning": float(total_earning),
            "period": f"Till {today.strftime('%d %b %y')}",
        }

        # 3. ATTENDANCE 
        attendance_records = TimeStamp.objects.filter(user=user, created_at__date=today)

        attendance = {
            "is_marked": attendance_records.exists(),
            "date": attendance_records.first().created_at.date() if attendance_records.exists() else None,
        }

        # 4. DISBURSEMENT (sum of approved application amounts from onboarding_v2)
        approved_apps_qs = (
            filter_applications(user, request.query_params)
            .filter(status=ApplicationStatus.APPROVED)
        )
        approved_amount = approved_apps_qs.aggregate(total=Sum("lead__amount"))["total"] or 0
        disbursement = {
            "current": float(approved_amount),
            "target": 1000000,
        }

        # 5. COUNTS
        leads_qs = filter_leads(user, request.query_params)
        applications_qs = filter_applications(user, request.query_params)
        total_leads = leads_qs.count()
        total_applications = applications_qs.count()

        # Filter active agents based on user role
        active_agents_qs = User.objects.filter(role=ROLES.AGENT.value, is_active=True)
        subtask_query = Q(assign_to=user)
        if user.role == ROLES.SALES_OFFICER.value:
            active_agents_qs = active_agents_qs.filter(assign_so=user)
            subtask_query = Q(assign_to=user) | Q(assign_to__assign_so=user)

        total_subtasks = SubTask.objects.filter(subtask_query).exclude(
            Q(status=SUBTASK_STATUS.DECLINED.value) | Q(task__status=TASK_STATUS.CLOSED.value)
        ).count()

        counts = {
            "total_leads": total_leads,
            "total_applications": total_applications,
            "active_agents": active_agents_qs.count(),
            "total_tasks": total_subtasks,
        }

        # 6. TASK SUMMARY
        pending = SubTask.objects.filter(
            subtask_query
        ).filter(
            Q(status=SUBTASK_STATUS.NEW_TASK.value) | Q(status__isnull=True)
        ).exclude(task__status=TASK_STATUS.CLOSED.value).count()

        in_progress = SubTask.objects.filter(
            subtask_query, status=SUBTASK_STATUS.IN_PROGRESS.value
        ).exclude(task__status=TASK_STATUS.CLOSED.value).count()

        completed = SubTask.objects.filter(
            subtask_query, status=SUBTASK_STATUS.COMPLETED.value
        ).exclude(task__status=TASK_STATUS.CLOSED.value).count()

        task_summary = {
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "total": total_subtasks,
        }

        # 7. IN-PROGRESS APPLICATIONS (from onboarding_v2)
        in_progress_qs = (
            filter_applications(user, request.query_params)
            .select_related("lead")
            .filter(
                status__in=[
                    ApplicationStatus.DRAFT,
                    ApplicationStatus.SENT_FOR_PRE_SCREENING,
                    ApplicationStatus.IN_PROGRESS,
                    ApplicationStatus.READY_FOR_LOAN,
                    ApplicationStatus.ELIGIBLE,
                ]
            )
            .order_by("-created_at")[:10]
        )

        in_progress_apps = []
        for app in in_progress_qs:
            lead = getattr(app, "lead", None)
            amount = getattr(lead, "amount", None)
            in_progress_apps.append(
                {
                    "customer_name": getattr(lead, "customer_name", "Unknown") if lead else "Unknown",
                    "created_at": app.created_at.isoformat() if getattr(app, "created_at", None) else None,
                    "customer_id": getattr(lead, "customer_id", None) if lead else None,
                    "application_id": app.application_id,
                    "appointment_time": None,
                    "loan_type": app.loan_type,
                    "lead_no": getattr(lead, "lead_code", None) if lead else None,
                    "application_no": app.application_id,
                    "amount": float(amount) if amount is not None else None,
                    "status": app.status,
                }
            )

        # 8. ALL AGENT APPLICATIONS (list of agents)

        # FINAL RESPONSE
        agents_qs = User.objects.filter(role=ROLES.AGENT.value, is_active=True).order_by("first_name", "last_name")
        if user.role == ROLES.SALES_OFFICER.value:
            agents_qs = agents_qs.filter(assign_so=user)
            
        agents_ser = UserResponseSerializer(agents_qs, many=True)
        return Response(
            {
                "status": "success",
                "data": {
                    "user": profile,
                    "earnings": earnings,
                    "attendance": attendance,
                    "disbursement": disbursement,
                    "counts": counts,
                    "task_summary": task_summary,
                    "in_progress_applications": in_progress_apps,
                    "all_agent": agents_ser.data
                },
            },
            status=status.HTTP_200_OK,
        )


class RHDashboardView(APIView):
    permission_classes = []

    def get(self, request):
        user = request.user
        if user.role != ROLES.REGIONAL_HEAD.value:
            return Response(
                {"status": "error", "message": "Only Regional Heads can access this dashboard"},
                status=status.HTTP_403_FORBIDDEN
            )

        today = timezone.localtime().date()

        # 1. USER PROFILE
        profile = {
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "city": user.city,
            "state": user.state,
        }

        # 2. GET MAPPED SOs
        mapped_sos = User.objects.filter(assign_so=user, role=ROLES.SALES_OFFICER.value)
        so_ids = list(mapped_sos.values_list('user_id', flat=True))

        # 3. GET MAPPED AGENTs (via SOs)
        mapped_agents = User.objects.filter(assign_so_id__in=so_ids, role=ROLES.AGENT.value)
        agent_ids = list(mapped_agents.values_list('user_id', flat=True))

        all_team_member_ids = so_ids + agent_ids

        # 4. COUNTS (Leads and Applications from all mapped members)
        leads_qs = LeadV2.objects.filter(Q(assigned_to_id__in=all_team_member_ids) | Q(created_by_id__in=all_team_member_ids))
        applications_qs = ApplicationV2.objects.filter(lead__id__in=leads_qs.values_list('id', flat=True))
        
        pending_approvals_qs = applications_qs.filter(status=ApplicationStatus.RH_APPROVAL_PENDING)

        # 5. BT TOTAL AMOUNT
        bt_total_amount = applications_qs.filter(loan_type=LeadType.BALANCE_TRANSFER).aggregate(total=Sum("lead__amount"))["total"] or 0

        counts = {
            "pending_approvals": pending_approvals_qs.count(),
            "total_leads": leads_qs.count(),
            "total_applications": applications_qs.count(),
            "bt_total_amount": float(bt_total_amount),
        }

        # 6. TEAM LIST (Mapped SOs and their individual stats)
        team_data = []
        for so in mapped_sos:
            so_team_ids = [so.user_id] + list(User.objects.filter(assign_so=so, role=ROLES.AGENT.value).values_list('user_id', flat=True))
            
            so_leads = LeadV2.objects.filter(Q(assigned_to_id__in=so_team_ids) | Q(created_by_id__in=so_team_ids))
            so_apps = ApplicationV2.objects.filter(lead__id__in=so_leads.values_list('id', flat=True))
            
            pending_apps_count = so_apps.filter(
                status__in=[
                    # ApplicationStatus.DRAFT,
                    # ApplicationStatus.SENT_FOR_PRE_SCREENING,
                    # ApplicationStatus.IN_PROGRESS,
                    # ApplicationStatus.READY_FOR_LOAN,
                    # ApplicationStatus.ELIGIBLE,
                    ApplicationStatus.SUBMITTED_TO_UNDERWRITING,
                ]
            ).count()

            # For Return Pending, we'll use a placeholder or check for CORRECTION status
            return_pending_amount = so_apps.filter(status=ApplicationStatus.CORRECTION).aggregate(total=Sum("lead__amount"))["total"] or 0

            team_data.append({
                "user_id": str(so.user_id),
                "full_name": f"{so.first_name} {so.last_name}".strip(),
                "employee_id": so.employee_id,
                "leads_count": so_leads.count(),
                "pending_applications": pending_apps_count,
                "return_pending_amount": float(return_pending_amount),
                "last_update": so.modified_at.isoformat() if hasattr(so, 'modified_at') and so.modified_at else None
            })

        return Response(
            {
                "status": "success",
                "data": {
                    "user": profile,
                    "counts": counts,
                    "team": team_data
                },
            },
            status=status.HTTP_200_OK,
        )
