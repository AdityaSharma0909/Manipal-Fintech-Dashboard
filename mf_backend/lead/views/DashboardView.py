from rest_framework.views import APIView

from account.serializers import AccountListAPISerializer
from application.serializers import ApplicationAllSerializer
from utils import helper
from utils.responseHandler import HttpResponse
import traceback
from ..models import Lead, LEAD_STATUS
from utils.constants import ROLES
from ..DataObjects import DashboardDataObjects
from application.models import Application, APPLICATION_STATUS
from ..serializers import DashboardSerializer
from django.db.models import Sum, Count, Value, IntegerField
from users.models import User
from loan.models import Loan
from users.models import TimeStamp
from django.utils import timezone
from datetime import date


class LeadDashboard(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            leads = Lead.objects.filter(assigned_to=user)
            total_no_of_leads = len(leads)

            total_account_created = len(
                list(
                    filter(
                        lambda x: x.assigned_to == user
                        and x.status == LEAD_STATUS.LEAD_ACCOUNT_CREATED.value,
                        leads,
                    )
                )
            )

            applicationDetails = {}

            total_loan_created = Loan.objects.filter(
                application__Originatedby=user
            ).count()

            # total_disbursed_amount = Application.objects.filter(
            #     Originatedby=user, status=APPLICATION_STATUS.LOAN_DISBURSED.value
            # ).aggregate(Sum("net_disbursed_amount"))

            # loan_managers = User.objects.filter(role=ROLES.LOAN_OFFICER.value)

            # leaderboardList = []
            # loan_managers_user_id = [str(x.user_id) for x in loan_managers]

            # disburse_data = Application.objects.filter(
            #     Originatedby__user_id__in=loan_managers_user_id,
            # ).annotate(
            #     total_loan_amount=Sum(
            #         "loan_amount", default=Value(0), output_field=IntegerField()
            #     ),
            #     total_application_created=Count("pk"),
            #     total_disbursed_amount=Sum(
            #         "disbursed_amount", default=Value(0), output_field=IntegerField()
            #     ),
            #     total_application_assets_net_weight=Sum(
            #         "net_weight", default=Value(0), output_field=IntegerField()
            #     ),
            # )

            # for loan_manager in loan_managers:
            #     app_details = list(
            #         filter(lambda x: x.Originatedby == loan_manager, disburse_data)
            #     )
            #     d = loan_manager.__dict__
            #     if len(app_details) > 0:
            #         total_disbursed_amount = sum(
            #             [
            #                 x.total_loan_amount
            #                 for x in app_details
            #                 if x.total_loan_amount is not None
            #             ]
            #         )
            #         if loan_manager == user:
            #             temp = app_details[0]
            #             applicationDetails = {
            #                 "total_loan_amount": temp.total_loan_amount,
            #                 "total_application_created": temp.total_application_created,
            #                 "total_disbursed_amount": temp.total_disbursed_amount,
            #                 "total_application_assets_net_weight": temp.total_application_assets_net_weight,
            #             }

            #     else:
            #         total_disbursed_amount = 0
            #     d["total_disbursed_amount"] = total_disbursed_amount
            #     leaderboardList.append(d)

            # recent_data = sorted(
            #     disburse_data, key=lambda x: x.created_at, reverse=True
            # )[:10]
            # recent_apps = [ApplicationAllSerializer(x).data for x in recent_data]
            # recent_accounts = [
            #     AccountListAPISerializer(x.account).data for x in recent_data
            # ]

            timestamps = TimeStamp.objects.filter(
                user=user,
                created_at__gte=timezone.localdate(),
            ).order_by("created_at")
            gold_rate_per_gram = helper.price_of_gold_22_karates()
            # application.gold_rate_per_gram=float(gold_rate_per_gram['gold_price__avg'])
            gold_rate_per_gram = gold_rate_per_gram
            lending_gold_rate = gold_rate_per_gram * (75 / 100)

            # TODO commented leaderboard, recent apps & accounts for now.
            dashboardObj = DashboardDataObjects(
                total_no_of_leads=total_no_of_leads,
                total_account_created=total_account_created,
                leads_to_be_covered=total_no_of_leads - total_account_created,
                total_loan_amount=applicationDetails.get("total_loan_amount", 0),
                total_application_created=applicationDetails.get(
                    "total_application_created", 0
                ),
                total_disbursed_amount=applicationDetails.get(
                    "total_disbursed_amount", 0
                ),
                total_application_assets_net_weight=applicationDetails.get(
                    "total_application_assets_net_weight", 0
                ),
                # total_disbursed_amount=total_disbursed_amount[
                #     "net_disbursed_amount__sum"
                # ],
                total_loan_created=total_loan_created,
                # leaderboard=leaderboardList,
                timestamps=timestamps,
                lending_gold_rate_per_gram=lending_gold_rate,
                gold_rate_per_gram=gold_rate_per_gram,
                # recent_apps=recent_apps,
                # recent_accounts=recent_accounts,
            )

            serializer = DashboardSerializer(dashboardObj)

            return HttpResponse.Success({"dashboard_data": serializer.data})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
