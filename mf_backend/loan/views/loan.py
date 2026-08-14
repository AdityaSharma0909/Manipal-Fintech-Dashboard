from django.db.models import Q
from rest_framework.views import APIView
from application.services.application_services import ApplicationHelper
from branch.models import BranchUserMapping
from branch.serializers import CreateBranchSerializer
from utils.constants import LOAN_TYPE, ROLES
from ..serializer import LoanAllSerializer
from utils.responseHandler import HttpResponse
import traceback
from ..models import Loan, LoanEMISchedule
from loan.serializer import LoanAssetSerializer
from ..services.demand_generation import DemandGeneration
from ..services.loan_services import LoanHelper
from rest_framework.pagination import PageNumberPagination, NotFound
from asset.services.asset_doc_service import AssetDocsService


class LoanView(APIView):

    def get(self, request):
        try:
            loan_id = request.GET.get("loan_id", "")
            loan = Loan.objects.get(loan_id=loan_id)
            loan_application = loan.application.application_id
            contra_loan = Loan.objects.exclude(loan_id=loan_id).filter(
                application__application_id=loan_application,
                loan_type=LOAN_TYPE.PERSONAL_LOAN.value,
            )
            personal_loan = {}
            contra_payoff = 0
            if len(contra_loan) > 0:
                personal_loan = LoanAllSerializer(contra_loan[0]).data
                pre_closure_payment = (
                    int(
                        personal_loan.get("application")
                        .get("product")
                        .get("pre_payment_col")
                    )
                    / 100
                ) * personal_loan.get("loan_amount")
                interest_accrued_till_date = (
                    personal_loan.get("interest_accrued_till_date", 0)
                    if personal_loan.get("interest_accrued_till_date") is not None
                    else 0
                )
                principal_remaining = (
                    personal_loan.get("principal_remaining", 0)
                    if personal_loan.get("principal_remaining") is not None
                    else 0
                )
                interest_paid = personal_loan.get("interest_paid", 0)
                interest_to_pay = abs(interest_paid - interest_accrued_till_date)
                contra_payoff = (
                    principal_remaining
                    + interest_to_pay
                    + personal_loan.get("penalty")
                    + pre_closure_payment
                )

            schedule = LoanEMISchedule.objects.filter(loan__loan_id=loan_id)
            if len(schedule) > 0:
                # due_dates=LoanHelper().get_next_due_date(schedule.first().data)
                # loan.due_date=due_dates.get('due_date')
                # loan.next_due_date=due_dates.get('next_due_date')
                # loan.current_emi=due_dates.get('current_installment')
                # loan.next_due_generation_date=due_dates.get('next_due_generation_date')
                # loan.save()
                DemandGeneration()
                schedule = schedule.first().data
            else:
                schedule = {}
            gold_loan = LoanAllSerializer(loan).data
            data = {"loan": gold_loan}
            data["personal_loan"] = personal_loan
            data["loan"]["schedule"] = schedule
            penalty = gold_loan.get("penalty")
            pre_closure_payment = (
                int(gold_loan.get("application").get("product").get("pre_payment_col"))
                / 100
            ) * gold_loan.get("loan_amount")

            interest_accrued_till_date = (
                gold_loan.get("interest_accrued_till_date", 0)
                if gold_loan.get("interest_accrued_till_date") is not None
                else 0
            )
            principal_remaining = (
                gold_loan.get("principal_remaining", 0)
                if gold_loan.get("principal_remaining") is not None
                else 0
            )
            interest_paid = gold_loan.get("interest_paid", 0)
            interest_to_pay = abs(interest_paid - interest_accrued_till_date)
            todays_payoff = (
                principal_remaining + interest_to_pay + penalty + pre_closure_payment
            )
            data["loan"]["todays_payoff"] = todays_payoff + contra_payoff
            data["loan"]["disbursals"] = ApplicationHelper().application_disbursals(
                loan.application.application_id
            )
            data["loan"]["branch_details"] = CreateBranchSerializer(
                loan.Originatedby.lm_branch_map.all().first().branch
            ).data
            # otherLenderAppraisalData = loan.other_lender_appraisal.all()
            # if len(otherLenderAppraisalData) > 0:
            #     data['loan']['other_lender_appraisal'] = OtherLenderAppraisalSerializer(otherLenderAppraisalData[0]).data

            return HttpResponse.Success(data)
        except Loan.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class LoanAllView(APIView, PageNumberPagination):

    def get(self, request):
        try:
            user = request.user
            role = request.user.role
            filters = request.query_params
            query = {}
            filter_option = [
                "lender",
                "product",
                "modified_at__gte",
                "modified_at__lte",
                "disbursed_date__gte",
                "disbursed_date__lte",
                "status",
                "amortization_type",
                "loan_type",
                "purpose_of_loan",
                "total_weight",
                "net_weight",
                "branch",
            ]

            if role == ROLES.LOAN_OFFICER.value:
                query["Originatedby"] = request.user
            elif (
                role == ROLES.ASSISTANT_BRANCH_MANAGER.value
                or role == ROLES.BRANCH_MANAGER.value
                or role == ROLES.CLUSTER_MANAGER.value
                or role == ROLES.REGIONAL_HEAD.value
                or role == ROLES.CREDIT_OFFICER.value
            ):
                branches = user.lm_branch_map.all()
                branches = [b.branch for b in branches]

                # userMap = BranchUserMapping.objects.filter(user=user)
                # if len(userMap) == 0:
                #     return HttpResponse.InternalServerError(
                #         "Branch User Mapping is not present for current user"
                #     )
                # branches = BranchUserMapping.objects.filter(branch=userMap[0].branch)
                # allBranchUsers = [b.user for b in branches]

                query["branch__in"] = branches
            elif role == ROLES.CUSTOMER.value:
                query["application__account__user"] = user

            for option in filter_option:
                opt = filters.get(option, None)
                if opt:
                    if option == "amortization_type":
                        query["application__amortization_type"] = opt
                    elif option == "purpose_of_loan":
                        query["application__purpose_of_loan"] = opt
                    elif option == "product":
                        query["application__product__product_name"] = opt
                    elif option == "lender":
                        query["application__lender__lender_name"] = opt
                    elif option == "branch":  # Handling branch filter
                        branches = opt.split(",")
                        query["branch__in"] = branches
                    else:
                        query[option] = opt

            exclude_list = [LOAN_TYPE.PERSONAL_LOAN.value]
            loans = (
                Loan.objects.exclude(Q(loan_type__in=exclude_list))
                .filter(Q(**query))
                .order_by("-modified_at")
            )

            # serializer = LoanAllSerializer(loans,many=True) //This exists in Existing code
            # data = serializer.data //This exists in Existing code
            # TODO remove this later
            if role == ROLES.LOAN_OFFICER.value:
                # for i in data: //This exists in Existing code
                for i in loans:
                    i["last_payment_date"] = None

            # pagination changes start
            try:
                paginated_data = self.paginate_queryset(loans, request)
                resp = LoanAllSerializer(paginated_data, many=True).data
                resp = self.get_paginated_response(resp).data
                resp["loans"] = resp.pop("results")
            except NotFound as err:
                print("page error::::")
                resp = {"loans": []}

            return HttpResponse.Success(resp)
            # pagination changes end

            # return HttpResponse.Success({"loans": data}) //This exists in Existing code
        except Loan.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        

class LoanAssetView(APIView):

    def get(self,request):
        try:
            loan_id = request.GET.get("loan_id", "")
            if not loan_id:
                return HttpResponse.BadRequest("loan ID is required")
            
            loan = Loan.objects.get(loan_id=loan_id)
            serializer = LoanAssetSerializer(loan)

            total_paid = loan.loan_amount - loan.principal_remaining
            payment_progress = (total_paid / loan.loan_amount) * 100 if loan.loan_amount != 0 else 0
            payment_progress = round(payment_progress, 2)
            
            response_data = {
                "loan": serializer.data,
                "payment_progress": payment_progress,
            }

            return HttpResponse.Success(response_data)
        except Loan.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))