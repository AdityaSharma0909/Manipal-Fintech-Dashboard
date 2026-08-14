"""
Dashboard Analytics Views
=========================
Four read-only endpoints that aggregate data from LeadV2, ApplicationV2, Loan
and User models for the analytics dashboard.

All endpoints:
  - Require X-Dashboard-API-Key header (bypassed in auth backend)
  - Accept optional query params:
      ?from_date=YYYY-MM-DD
      ?to_date=YYYY-MM-DD
  - Team endpoint additionally accepts:
      ?branch_id=<uuid>

Response format is always JSON.
"""

from datetime import date, datetime, timedelta

from django.db.models import (
    Avg, Case, Count, DecimalField, ExpressionWrapper, F, FloatField,
    IntegerField, Q, Sum, Value, When,
)
from django.db.models.functions import Coalesce, TruncDate, TruncMonth
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.auth import DashboardAPIKeyAuthentication

# Lenders we want to break out individually
TRACKED_LENDERS = ["AXIS", "ICICI", "FEDERAL"]

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_date_range(request):
    """Parse ?from_date / ?to_date query params into (date|None, date|None)."""
    from_date = request.query_params.get("from_date")
    to_date = request.query_params.get("to_date")
    from_dt = parse_date(from_date) if from_date else None
    to_dt = parse_date(to_date) if to_date else None
    return from_dt, to_dt


def _apply_date_filter(qs, field: str, from_dt, to_dt):
    """Apply created_at (or any datetime field) range filter to a queryset."""
    if from_dt:
        qs = qs.filter(**{f"{field}__date__gte": from_dt})
    if to_dt:
        qs = qs.filter(**{f"{field}__date__lte": to_dt})
    return qs


# ──────────────────────────────────────────────────────────────────────────────
# 1. Leads  ─  GET /dashboard/leads/
# ──────────────────────────────────────────────────────────────────────────────

class LeadStatsView(APIView):
    """
    Aggregated lead statistics (using onboarding_v2.models.LeadV2).
    """

    authentication_classes = [DashboardAPIKeyAuthentication]
    permission_classes = []

    def get(self, request):
        from onboarding_v2.models import LeadV2

        from_dt, to_dt = _get_date_range(request)

        lead_qs = LeadV2.objects.all()
        lead_qs = _apply_date_filter(lead_qs, "created_at", from_dt, to_dt)

        total_leads = lead_qs.count()

        by_status = list(
            lead_qs.values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        by_source = list(
            lead_qs.values("source")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        by_lending_type = list(
            lead_qs.values(lending_type=F("lead_type"))
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # External/Digital/Partner leads
        external_lead_qs = lead_qs.filter(source__in=["Digital", "Partner", "Web", "Agent"])
        total_external = external_lead_qs.count()
        disbursed_count = external_lead_qs.filter(status="DISBURSED").count()
        conversion_rate = round(
            (disbursed_count / total_external * 100) if total_external > 0 else 0.0, 2
        )

        by_loan_type = list(
            external_lead_qs.values(loan_type=F("product_subcategory"))
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        by_new_status = list(
            external_lead_qs.values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Monthly trend (last 6 months)
        six_months_ago = date.today() - timedelta(days=180)
        monthly_trend = list(
            LeadV2.objects.filter(created_at__date__gte=six_months_ago)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
            .values("month", "count")
        )
        monthly_trend = [
            {"month": entry["month"].strftime("%Y-%m"), "count": entry["count"]}
            for entry in monthly_trend
        ]

        return Response({
            "classic_leads": {
                "total": total_leads - total_external,
                "by_status": by_status,
                "by_source": by_source,
                "by_lending_type": by_lending_type,
            },
            "external_leads": {
                "total": total_external,
                "disbursed": disbursed_count,
                "conversion_rate_pct": conversion_rate,
                "by_loan_type": by_loan_type,
                "by_status": by_new_status,
            },
            "combined_total": total_leads,
            "monthly_trend": monthly_trend,
        })


# ──────────────────────────────────────────────────────────────────────────────
# 2. Applications  ─  GET /dashboard/applications/
# ──────────────────────────────────────────────────────────────────────────────

class ApplicationStatsView(APIView):
    """
    Aggregated application statistics (using onboarding_v2.models.ApplicationV2).
    """

    authentication_classes = [DashboardAPIKeyAuthentication]
    permission_classes = []

    def get(self, request):
        from onboarding_v2.models import ApplicationV2

        from_dt, to_dt = _get_date_range(request)

        qs = ApplicationV2.objects.all()
        qs = _apply_date_filter(qs, "created_at", from_dt, to_dt)

        total = qs.count()

        by_status = list(
            qs.values("status")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        by_loan_type = list(
            qs.values(application_loan_type=F("loan_type"))
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Applications per lender
        by_lender = list(
            qs.filter(lending_partner__isnull=False)
            .values(lender_name=F("lending_partner"))
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Break out the key lenders
        tracked = {}
        for lender_key in TRACKED_LENDERS:
            tracked[lender_key] = qs.filter(
                lending_partner__icontains=lender_key
            ).count()

        # Disbursed V2 applications
        disbursed_count = qs.filter(status="DISBURSED").count()

        # Bureau approval rate
        approved_count = qs.filter(bureau_decision="APPROVE").count()
        bureau_approval_rate = round(
            (approved_count / total * 100) if total > 0 else 0.0, 2
        )

        # Monthly trend
        six_months_ago = date.today() - timedelta(days=180)
        monthly_trend = list(
            ApplicationV2.objects.filter(created_at__date__gte=six_months_ago)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
            .values("month", "count")
        )
        monthly_trend = [
            {"month": e["month"].strftime("%Y-%m"), "count": e["count"]}
            for e in monthly_trend
        ]

        return Response({
            "total_applications": total,
            "disbursed_count": disbursed_count,
            "bureau_approval_rate_pct": bureau_approval_rate,
            "by_status": by_status,
            "by_loan_type": by_loan_type,
            "by_lender": by_lender,
            "tracked_lenders": tracked,
            "monthly_trend": monthly_trend,
        })


# ──────────────────────────────────────────────────────────────────────────────
# 3. Loans  ─  GET /dashboard/loans/
# ──────────────────────────────────────────────────────────────────────────────

NPA_THRESHOLD_DAYS = 90

class LoanStatsView(APIView):
    """
    Aggregated loan portfolio statistics.
    """

    authentication_classes = [DashboardAPIKeyAuthentication]
    permission_classes = []

    def get(self, request):
        from loan.models import Loan

        from_dt, to_dt = _get_date_range(request)

        qs = Loan.objects.select_related("lender", "product").all()
        if from_dt:
            qs = qs.filter(disbursed_date__date__gte=from_dt)
        if to_dt:
            qs = qs.filter(disbursed_date__date__lte=to_dt)

        agg = qs.aggregate(
            total_loans=Count("loan_id"),
            active_loans=Count(
                "loan_id",
                filter=Q(status__in=["Active - Good Standing", "Active - Bad Standing", "ACTIVE"]),
            ),
            npa_count=Count(
                "loan_id",
                filter=Q(days_past_dues__gt=NPA_THRESHOLD_DAYS) | Q(status="NPA"),
            ),
            total_disbursed=Coalesce(
                Sum("disbursed_amount"), Value(0), output_field=IntegerField()
            ),
            total_principal_remaining=Coalesce(
                Sum("principal_remaining"), Value(0.0), output_field=FloatField()
            ),
            total_interest_remaining=Coalesce(
                Sum("interest_remaining"), Value(0.0), output_field=FloatField()
            ),
            avg_loan_amount=Coalesce(
                Avg("loan_amount"), Value(0.0), output_field=FloatField()
            ),
        )

        by_status = list(
            qs.values("status")
            .annotate(count=Count("loan_id"))
            .order_by("-count")
        )

        by_lender = list(
            qs.filter(lender__isnull=False)
            .values(lender_name=F("lender__lender_name"))
            .annotate(count=Count("loan_id"), total_disbursed=Sum("disbursed_amount"))
            .order_by("-count")
        )

        by_loan_type = list(
            qs.values("loan_type")
            .annotate(count=Count("loan_id"))
            .order_by("-count")
        )

        # Monthly disbursal trend (last 6 months)
        six_months_ago = date.today() - timedelta(days=180)
        monthly_disbursals = list(
            Loan.objects.filter(disbursed_date__date__gte=six_months_ago)
            .annotate(month=TruncMonth("disbursed_date"))
            .values("month")
            .annotate(
                count=Count("loan_id"),
                total_amount=Coalesce(Sum("disbursed_amount"), Value(0), output_field=IntegerField()),
            )
            .order_by("month")
            .values("month", "count", "total_amount")
        )
        monthly_disbursals = [
            {
                "month": e["month"].strftime("%Y-%m"),
                "count": e["count"],
                "total_amount_inr": e["total_amount"],
            }
            for e in monthly_disbursals
        ]

        return Response({
            "total_loans": agg["total_loans"],
            "active_loans": agg["active_loans"],
            "npa_count": agg["npa_count"],
            "npa_threshold_days": NPA_THRESHOLD_DAYS,
            "total_disbursed_inr": agg["total_disbursed"],
            "total_principal_remaining_inr": round(agg["total_principal_remaining"] or 0, 2),
            "total_interest_remaining_inr": round(agg["total_interest_remaining"] or 0, 2),
            "avg_loan_amount_inr": round(agg["avg_loan_amount"] or 0, 2),
            "by_status": by_status,
            "by_lender": by_lender,
            "by_loan_type": by_loan_type,
            "monthly_disbursals": monthly_disbursals,
        })


# ──────────────────────────────────────────────────────────────────────────────
# 4. Team  ─  GET /dashboard/team/
# ──────────────────────────────────────────────────────────────────────────────

class TeamStatsView(APIView):
    """
    Team performance statistics.
    """

    authentication_classes = [DashboardAPIKeyAuthentication]
    permission_classes = []

    def get(self, request):
        from onboarding_v2.models import LeadV2, ApplicationV2
        from branch.models import Branch

        from_dt, to_dt = _get_date_range(request)
        branch_id = request.query_params.get("branch_id")

        # ── Leads per Loan Officer ──────────────────────────────────────────
        lead_qs = LeadV2.objects.filter(assigned_to__isnull=False)
        lead_qs = _apply_date_filter(lead_qs, "created_at", from_dt, to_dt)
        if branch_id:
            lead_qs = lead_qs.filter(
                assigned_to__lm_branch_map__branch_id=branch_id
            )

        leads_raw = list(
            lead_qs.values(
                "assigned_to__user_id",
                "assigned_to__first_name",
                "assigned_to__last_name",
                "assigned_to__role",
            )
            .annotate(lead_count=Count("id"))
            .order_by("-lead_count")[:50]
        )

        leads_per_officer = [
            {
                "officer_id": row["assigned_to__user_id"],
                "first_name": row["assigned_to__first_name"],
                "last_name": row["assigned_to__last_name"],
                "role": row["assigned_to__role"],
                "lead_count": row["lead_count"],
            }
            for row in leads_raw
        ]

        # ── Conversions per Branch (mapped dynamically by pincode) ──────────
        branches = {b.branch_name: b for b in Branch.objects.all()}
        branch_stats = {
            b.branch_id: {
                "branch_id": str(b.branch_id),
                "branch_name": b.branch_name,
                "branch_code": b.branch_code,
                "total_applications": 0,
                "disbursed": 0,
                "latitude": b.latitude,
                "longitude": b.longitude,
            } for b in branches.values()
        }

        app_qs = ApplicationV2.objects.select_related("lead").all()
        app_qs = _apply_date_filter(app_qs, "created_at", from_dt, to_dt)

        if branch_id:
            branch_stats = {k: v for k, v in branch_stats.items() if str(k) == branch_id}

        for app in app_qs:
            pincode = app.lead.pincode or ""
            target_branch = None
            if pincode.startswith("560"):
                target_branch = branches.get("Bangalore Central")
            elif pincode.startswith("400"):
                target_branch = branches.get("Mumbai South")
            elif pincode.startswith("110"):
                target_branch = branches.get("Delhi Connaught Place")
            elif pincode.startswith("600"):
                target_branch = branches.get("Chennai T-Nagar")
            elif pincode.startswith("500"):
                target_branch = branches.get("Hyderabad Gachibowli")

            if target_branch and target_branch.branch_id in branch_stats:
                stats = branch_stats[target_branch.branch_id]
                stats["total_applications"] += 1
                if app.status == "DISBURSED":
                    stats["disbursed"] += 1

        conversions_per_branch = []
        for stats in branch_stats.values():
            total = stats["total_applications"]
            disbursed = stats["disbursed"]
            stats["conversion_rate_pct"] = round(
                (disbursed / total * 100) if total > 0 else 0.0, 2
            )
            conversions_per_branch.append(stats)
            
        conversions_per_branch.sort(key=lambda x: x["disbursed"], reverse=True)

        # ── Approvals per BM (assigned_rh) ──────────────────────────────────
        rh_qs = ApplicationV2.objects.filter(assigned_rh__isnull=False)
        rh_qs = _apply_date_filter(rh_qs, "created_at", from_dt, to_dt)
        if branch_id:
            rh_qs = rh_qs.filter(assigned_rh__lm_branch_map__branch_id=branch_id)

        approvals_raw = list(
            rh_qs.values(
                "assigned_rh__user_id",
                "assigned_rh__first_name",
                "assigned_rh__last_name",
            )
            .annotate(approved_count=Count("id"))
            .order_by("-approved_count")[:30]
        )

        approvals_per_bm = [
            {
                "bm_id": row["assigned_rh__user_id"],
                "first_name": row["assigned_rh__first_name"],
                "last_name": row["assigned_rh__last_name"],
                "approved_count": row["approved_count"],
            }
            for row in approvals_raw
        ]

        # ── Top 5 Performers ────────────────────────────────────────────────
        top_performers = leads_per_officer[:5]

        from django.contrib.auth import get_user_model
        from users.models import TimeStamp
        timestamp_qs = TimeStamp.objects.all()
        timestamp_qs = _apply_date_filter(timestamp_qs, "created_at", from_dt, to_dt)
        total_sessions = timestamp_qs.count()
        total_unique = timestamp_qs.values("user").distinct().count()

        return Response({
            "leads_per_officer": leads_per_officer,
            "conversions_per_branch": conversions_per_branch,
            "approvals_per_bm": approvals_per_bm,
            "top_performers": top_performers,
            "total_users": total_sessions, # Total sessions & repeat access events from TimeStamp
            "unique_users": total_unique,  # Distinct individual users counted once from TimeStamp
            "registered_staff": get_user_model().objects.count(),
            "total_branches": Branch.objects.count(),
        })
