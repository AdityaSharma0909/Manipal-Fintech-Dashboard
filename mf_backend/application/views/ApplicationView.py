from django.db.models import Q, Case, When, Value, BooleanField
from rest_framework.views import APIView
from rest_framework.response import Response

from asset.models import Asset
from loan.models import LoanEMISchedule
from loan.services.loan_emi_record_service import LoanEmiService
from utils.envSetup import environment
from ..serializers import (
    ApplicationModelSerializer,
    CreatApplicationSerializer,
    ApplicationOverviewSerializer,
    ApplicationListSerializer,
    AddLoanAPISerializer,
)
from ..models import Application, ApplicationGoodsMapping, LoanDocument
from utils.responseHandler import HttpResponse
from utils import constants, helper
import logging
from dateutil import parser as parser
from rest_framework import status
from django.conf import settings
import traceback
from account.models import Account
from ..service import ApplicationService
from product.models import Product
from branch.models import BranchUserMapping
from utils.constants import ROLES, APPLICATION_STATUS, PurposeOfLoan, ApplicationType , LENDING_TYPE , LOAN_TYPE , PRODUCT_TYPE , AMORTIZATIONTYPE , PERIOD
from utility.response_handler import HttpResponse as resp
from ..services.application_services import ApplicationHelper
from decimal import Decimal 


class ApplicationViewAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            user = request.user
            account = Account.objects.get(account_id=request.GET.get("account_id", ""))
            data[
                "application_number"
            ] = ApplicationService().generate_application_number()
            data["account"] = str(account)
            data["status"] = constants.APPLICATION_STATUS.NEW_APPLICATION.value
            data["Originatedby"] = request.user.user_id
            branch=request.user.lm_branch_map.all().first()
            print('branch================>',branch)
            if branch:
                data['branch']=branch.branch_id
            else:
                data['branch']=branch
            if data['product']:
                product = Product.objects.get(pk=data['product'])
                data['tenure'] = product.tenure
                data['intrest_rate'] = product.interest_rate
                data['processing_fee_percent'] = product.processing_fee
                data['penalty_percent'] = product.penalty
                data['repayment_frequency'] = product.period
                data['lender'] = product.lender.lender_id
                data['amortization_type'] = product.amortization_type
                if user.role in [ROLES.LOAN_OFFICER.value , ROLES.BRANCH_MANAGER.value]:
                    gold_rate_per_gram = helper.price_of_gold_22_karates()
                    data['gold_rate_per_gram'] = gold_rate_per_gram
                    lendingGoldRate = round(gold_rate_per_gram * float(product.ltv_percentage / 100), 0)
                    data['lending_gold_rate_per_gram']=lendingGoldRate
                    if product.product_type==LOAN_TYPE.WELLNESS.value:
                        data['application_loan_type'] = LENDING_TYPE.WELLNESS.value
                        data['loan_amount'] = 0
                        data['amortization_type'] = AMORTIZATIONTYPE.NONE.value
                        data['repayment_frequency'] = PERIOD.NONE.value
                    else:
                        data['application_loan_type'] = LENDING_TYPE.GOLD_LOAN.value

                elif user.role == ROLES.RELATIONSHIP_MANAGER.value:
                    data['gold_rate_per_gram'] = 0
                    data['lending_gold_rate_per_gram'] = 0  
                    if product.product_type==LOAN_TYPE.MSME_UNSECURED.value:
                        data['application_loan_type'] = LENDING_TYPE.MSME_UNSECURED.value
                    elif product.product_type==LOAN_TYPE.MSME_UNSECURED_AGRI.value:
                        data['application_loan_type'] = LENDING_TYPE.MSME_UNSECURED_AGRI.value
                    data['loan_amount'] = 0



            serializer = CreatApplicationSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"application": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

        # print(data)
        # data["user"]=user

        # print(user)
        # return Response("This is a test")

    def get(self, request):
        user = request.user
        query={}
        pg = request.GET.get('pg', None)
        page_no = 1
        offset = 0
        page_limit = int(settings.API_PAGE_SIZE)
        status = request.GET.get('status', None)
        date = request.GET.get('date', None)
        loan_type_param = request.GET.get('application_loan_type', None)
        params=request.query_params
        data=[]
        if pg is not None:
            try:
                page_no = int(pg)
                offset = (page_no - 1) * page_limit
            except ValueError as ve:
                return HttpResponse.BadRequest("Please send correct 'pg' param.")
        for param, value in params.items():
            if param=='created_at__gte':
                query['created_at__date__gte']=value
            elif param=='created_at__lte':
                query['created_at__date__lte'] = value
        print(user.role)
        if status is not None:
            query['status__in'] = status.split(",")
        if date is not None:
            query['created_at__date'] = parser.parse(str(date)).date()
        print(query)
        if user.role == ROLES.LOAN_OFFICER.value:
            query['Originatedby'] = user
            # TODO no filtering for LMs
            if pg:
                data=Application.objects.filter(Q(**query)).annotate(
                         show_inspection_screen=Case(
                            When(
                                loan_take_over_app__requested_amount_from_radian__gte=int(environment.REQUEST_LOAN_AMOUNT_CHECK),
                                then=Value(True)
                            ),
                            default=Value(False),
                            output_field=BooleanField()
                        )
                    ).order_by('-modefied_at')[offset: offset + page_limit]
            else:

                data = Application.objects.filter(Q(**query)) \
                .annotate(
                         show_inspection_screen=Case(
                When(
                    loan_take_over_app__requested_amount_from_radian__gte=int(environment.REQUEST_LOAN_AMOUNT_CHECK),
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        ) \
    .order_by('-modefied_at')
        elif (
            user.role == ROLES.ASSISTANT_BRANCH_MANAGER.value
            or user.role == ROLES.BRANCH_MANAGER.value
            or user.role == ROLES.CLUSTER_MANAGER.value
            or user.role == ROLES.REGIONAL_HEAD.value
            or user.role==ROLES.BRANCH_OPERATION_MANAGER.value
            or user.role == ROLES.CREDIT_OFFICER.value
            # or user.role==ROLES.BUSINESS_HEAD.value
        ):
            userMap = BranchUserMapping.objects.filter(user=user)
            if len(userMap) == 0:
                return HttpResponse.InternalServerError(
                    "Branch User Mapping is not present for current user"
                )

            branches = BranchUserMapping.objects.filter(branch=userMap[0].branch)
            allBranchUsers = [b.user for b in branches]
            query['Originatedby__in']=allBranchUsers


            data = Application.objects.filter(Q(**query)).order_by('-modefied_at')[offset: offset + page_limit]
        elif user.role == ROLES.CPC.value or \
             user.role==ROLES.CHIEF_BUSINESS_OPERATOR.value \
             or user.role==ROLES.BUSINESS_HEAD.value or user.role==ROLES.AUDIT_ADMIN.value:
            branch=request.GET.get('branch', None)
            if branch is not None:
                branches = BranchUserMapping.objects.filter(branch__branch_code=branch)
                allBranchUsers = [b.user for b in branches]
                query['Originatedby__in']=allBranchUsers

            if date is not None:
                query['created_at__date']=date
            
            if loan_type_param == LENDING_TYPE.GOLD_LOAN.value:
                query['application_loan_type'] = LENDING_TYPE.GOLD_LOAN.value
            elif loan_type_param == LENDING_TYPE.MSME_UNSECURED.value:
                query['application_loan_type'] = LENDING_TYPE.MSME_UNSECURED.value
            elif loan_type_param == LENDING_TYPE.WELLNESS.value:
                query['application_loan_type'] = LENDING_TYPE.WELLNESS.value
            elif loan_type_param == LENDING_TYPE.MSME_UNSECURED_AGRI.value:
                query['application_loan_type'] = LENDING_TYPE.MSME_UNSECURED_AGRI.value     

            if len(query)>0:
                data=Application.objects.filter(Q(**query)).order_by('-modefied_at')[offset: offset + page_limit]
            else:
                data=Application.objects.all().order_by('-modefied_at')[offset:offset + page_limit]
            # TODO: why we are doing order_by again in below line
            # data=list(data.order_by("-created_at"))
        elif user.role == ROLES.CREDIT_MANAGER.value:

            if loan_type_param == LENDING_TYPE.MSME_UNSECURED.value:
                query['application_loan_type'] = LENDING_TYPE.MSME_UNSECURED.value
                data = Application.objects.filter(Q(**query)).order_by('-modefied_at')[offset: offset + page_limit]
            elif loan_type_param == LENDING_TYPE.MSME_UNSECURED_AGRI.value:
                query['application_loan_type'] = LENDING_TYPE.MSME_UNSECURED_AGRI.value
                data = Application.objects.filter(Q(**query)).order_by('-modefied_at')[offset: offset + page_limit]
        elif user.role == ROLES.RELATIONSHIP_MANAGER.value:
            data = Application.objects.filter(Originatedby=request.user, **query).order_by('-modefied_at')
        else:
            data = []
        # print(data)
        # if user.role == ROLES.CPC.value:
        #     serializer = ApplicationAllSerializer(data, many=True)
        # else:
        # serializer = ApplicationOverviewSerializer(data, many=True)
        serializer = ApplicationListSerializer(data, many=True)
        return HttpResponse.Success(serializer.data)

    def patch(self, request, *args, **kwargs):
        data = request.data
        application_id = str(
            Application.objects.get(
                application_id=request.GET.get("application_id", "")
            )
        )
        if not application_id:
            return Response(
                {"error": constants.APPLICATION_ID_NOT_NULL}, status=status.HTTP_200_OK
            )
        # Update application status logic
        
        try:
            application = Application.objects.get(application_id=application_id)
            if application.status == APPLICATION_STATUS.APPLICATION_SENT_TO_CO.value:
                application.status = APPLICATION_STATUS.APPLICATION_INITIATED.value
                application.save()
            acc_ser = ApplicationModelSerializer(application, data=data, partial=True)
            if acc_ser.is_valid():
                acc_ser.save()
                resp = Response(
                    {"status": "success", "data": acc_ser.data},
                    status=status.HTTP_200_OK,
                )

            else:
                resp = Response({"errors": acc_ser.errors}, status=status.HTTP_200_OK)

            return resp
        except Exception as ve:
            return Response({"error": str(ve)}, status=status.HTTP_200_OK)

    def delete(self, request):
        application_id = request.data.get('application_id', None)
        if application_id is None:
            return resp().response(code=400, data=None, error_msg='application_id required', error_code=400)
        application_service = ApplicationHelper().delete(application_id=application_id)
        return resp().response(code=application_service.get('status_code'),
                               data=application_service.get('data'),
                               error_code=application_service.get('status_code'),
                               error_msg=application_service.get('data')
                               )
class AmortizationView(APIView):
    def get(self, request):
        app_id = str(request.GET.get("app_id"))
        schedule=LoanEmiService().create_or_get_schedule(app_id)
        return HttpResponse.Success({"schedule": schedule})


class UpdateApplicationProductView(APIView):
    # def patch(self, request, *args, **kwargs):
    #     data = request.data
    #     application_id = request.GET.get("application_id", None)
    #     # product_id = request.GET.get('product_id',None)
    #     if not application_id:
    #         return Response(
    #             {"error": constants.APPLICATION_ID_NOT_NULL}, status=status.HTTP_200_OK
    #         )

    #     try:
    #         app = Application.objects.get(application_id=application_id)
    #         app=self.__clear_previous_data(app)
    #         product = Product.objects.get(product_id=data.get("product_id"))
    #         data["product"] = product.product_id
    #         data['tenure'] = product.tenure
    #         data['intrest_rate'] = product.interest_rate
    #         data['processing_fee_percent'] = product.processing_fee
    #         data['penalty_percent'] = product.penalty
    #         data['repayment_frequency'] = product.period
    #         data['lender'] = product.lender.lender_id
    #         data['amortization_type'] = product.amortization_type
    #         app_ser = AddLoanAPISerializer(app, data=data, partial=True)
    #         if app_ser.is_valid():
    #             app_ser.save()
    #             resp = Response(
    #                 {
    #                     "status": "success",
    #                 },
    #                 status=status.HTTP_200_OK,
    #             )
    #         else:
    #             resp = Response({"errors": app_ser.errors}, status=status.HTTP_200_OK)

    #         return resp
    #     except Exception as ve:
    #         return Response({"error": str(ve)}, status=status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        data = request.data
        application_id = request.GET.get("application_id", None)
        
        if not application_id:
            return Response(
                {"error": constants.APPLICATION_ID_NOT_NULL}, status=status.HTTP_200_OK
            )

        try:
            app = Application.objects.get(application_id=application_id)
            
            if app.status not in [APPLICATION_STATUS.NEW_APPLICATION.value, APPLICATION_STATUS.TAKEOVER_FIRST_DISBURSEMENT_DONE.value ,APPLICATION_STATUS.ASSET_ADDED.value, APPLICATION_STATUS.LOAN_AMOUNT_ADDED.value, APPLICATION_STATUS.TELE_VERIFICATION_DONE.value]:
                return Response(
                    {"error": "Product can only be changed when the status is NEW_APPLICATION, ASSET_ADDED, LOAN_AMOUNT_ADDED, TAKEOVER_DONE, TELE_VERIFICATION_DONE"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product_id = data.get("product_id")
            if not product_id:
                return Response(
                    {"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST
                )
            
            product = Product.objects.get(product_id=product_id)

            if app.application_loan_type==LOAN_TYPE.GOLD_LOAN.value:
            
                if product.product_type != 'GOLD_LOAN' or not product.active:
                    return Response(
                        {"error": "Product type should be GOLD LOAN and it should be active to change the product"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                
            elif app.application_loan_type==LOAN_TYPE.MSME_UNSECURED.value:
            
                if product.product_type != 'MSME_UNSECURED' or not product.active:
                    return Response(
                        {"error": "Product type should be MSME UNSECURED and it should be active to change the product"},
                        status=status.HTTP_400_BAD_REQUEST
                    )


            app = self.__clear_previous_data(app)
            
            # Update application fields with new product details
            app.product = product
            app.tenure = product.tenure
            app.ltv = product.ltv_percentage
            app.intrest_rate = product.interest_rate
            app.processing_fee_percent = product.processing_fee
            app.penalty_percent = product.penalty
            app.repayment_frequency = product.period
            app.lender = product.lender
            app.amortization_type = product.amortization_type

            if app.application_type == ApplicationType.NEW.value and app.application_loan_type==LOAN_TYPE.GOLD_LOAN.value:
                app.status=APPLICATION_STATUS.ASSET_ADDED.value

                # Calculate eligible amount based on the new product
                asset_value = app.total_asset_price
                if asset_value is not None and product.ltv_percentage is not None:
                    eligible_amount = Decimal(asset_value) * Decimal(product.ltv_percentage) / 100
                    app.eligible_amount = eligible_amount
            
            
            app.save()
            
            resp = Response({"status": "success"}, status=status.HTTP_200_OK)
            
        except Application.DoesNotExist:
            resp = Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            resp = Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ve:
            resp = Response({"error": str(ve)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return resp

    def __clear_previous_data(self, app):
        app.loan_amount = 0
        app.purpose_of_loan = PurposeOfLoan.OTHER.value
        app.net_disbursed_amount = 0
        app.disbursed_amount = 0
        app.disbursal_amount = 0
        app.contra_loan_amount = 0
        app.processing_fee = 0
        app.processing_fee_percent = 0
        app.contra_loan_processing_fee = 0
        app.contra_loan_processing_fee_amount = 0
        app.contra_loan_net_payable_balance = 0
        app.contra_loan_stamp_duty_amount = 0
        app.save()
        
        ApplicationGoodsMapping.objects.filter(application__application_id=app.application_id).delete()
        LoanEMISchedule.objects.filter(loan__application__application_id=app.application_id).delete()
        LoanDocument.objects.filter(document_type='FINCARE_PLEDGE_CARD', application__application_id=app.application_id).delete()
        return app
