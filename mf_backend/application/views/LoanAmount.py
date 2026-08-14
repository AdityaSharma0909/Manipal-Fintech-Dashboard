from rest_framework.views import APIView

from django.db.models import Q
from asset.services.asset_service import AssetService
from loan.services.loan_services import LoanHelper
from ..models  import Application, ApplicationGoodsMapping
from product.models import WhiteGoods
from utils.constants import PERIOD, ApplicationType , ROLES , LENDING_TYPE , PurposeOfLoan
from utils.responseHandler import HttpResponse
from ..serializers import AddLoanAPISerializer,AddGoodsAPISerializer,AddRequestedAmountAPISerializer
from utils.constants import APPLICATION_STATUS
from product.serializers import WhiteGoodsSerializer
from asset.models import Asset
from branch.models import BranchProductMapping ,BranchUserMapping
from django.db import transaction
from users.service.fcmService import FCMService
from utils.envSetup import environment
import utils.helper as helper
import traceback

from ..service import ApplicationService
from ..services.application_services import ApplicationHelper


class LoanAmountView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            application = Application.objects.get(application_id=request.GET.get('application_id',''))
            if user.role in [ROLES.LOAN_OFFICER.value, ROLES.BRANCH_MANAGER.value]:
                loan_amount= request.data["loan_amount"]
                contraLoanBaseAmount = request.data.get("contra_loan_amount", 0)
                loan_eligibility=LoanHelper().check_loan_amount_pan_eligibility(amount_request=loan_amount+contraLoanBaseAmount,
                                                                                amount_requested_by=application.account)
                if loan_eligibility.get('status_code')==403 :
                    return HttpResponse.Success({'msg':loan_eligibility.get('data')})
                asset=Asset.objects.filter(application=application)
                total_asset_gold=0
                for i in asset:
                    all_docs_uploaded=AssetService().check_all_assets_uploaded(asset=i)
                    if all_docs_uploaded:
                        total_asset_gold+=i.net_weight
                    else:
                        return HttpResponse.Success({'msg':f'Please update asset type {i.type} with all asset document'})



                if application.product:
                    if loan_amount>application.product.maximum_ticket_size:
                        return HttpResponse.BadRequest(f"Loan Amount should be less than or equal to  {application.product.maximum_ticket_size} rs ticket size.")
                    if loan_amount<application.product.minimum_ticket_size:
                        return HttpResponse.BadRequest(f"Loan Amount should be greater than or equal to  {application.product.minimum_ticket_size} rs ticket size.")

                purpose_of_loan= request.data["purpose_of_loan"]
                allowed_purposes = [
                        PurposeOfLoan.EDUCATIONAL.value, PurposeOfLoan.MARRIAGE.value, PurposeOfLoan.INCOME_GENERATION.value, PurposeOfLoan.MEDICAL_EMERGENCY.value,
                        PurposeOfLoan.BROAD_CATEGORY.value, PurposeOfLoan.PURCHASE_OF_ASSETS.value, PurposeOfLoan.PURCHASE_OF_GOODS.value, PurposeOfLoan.LAND_DEVELOPMENT.value, PurposeOfLoan.PURCHASE_OF_SEEDS.value, 
                        PurposeOfLoan.PLANTATION_EXPENSES.value, PurposeOfLoan.PURCHASE_OF_AGRICULTURAL_EQUIPMENTS.value,PurposeOfLoan.PAYMENT_OF_LABOUR_EXPENSES.value, PurposeOfLoan.MEDICAL_EXPENSES.value, 
                        PurposeOfLoan.TRAVEL_EXPENSES.value, PurposeOfLoan.OTHER.value , 
                    ]
                print(purpose_of_loan)
                if purpose_of_loan not in allowed_purposes:
                    return HttpResponse.BadRequest("Invalid Choice")
                # if request.data["goods"]:
                #     goods=WhiteGoods.objects.get(goods_id= request.data["goods"])
                #     application.goods=goods
                #     application.save()
                # print(request.data["goods"])
                # print(type(request.data["goods"]))


                application.status = APPLICATION_STATUS.LOAN_AMOUNT_ADDED.value
                application.loan_amount=int(loan_amount)
                application.purpose_of_loan=purpose_of_loan
                # application.application_loan_type = LENDING_TYPE.GOLD_LOAN.value
                
                application.processing_fee=float(application.product.processing_fee)*(application.loan_amount)/100
                application.current_gst_rate = float(environment.CURRENT_GTS_RATE)
                application.gst = (application.current_gst_rate/100) * application.processing_fee
                
                try:
                    # branch=BranchUserMapping.objects.get(user=request.user).branch
                    query = Q(minimum_amount__lte=application.loan_amount) & Q( Q(maximum_amount__isnull=True) | Q(maximum_amount__gte=application.loan_amount) )
                    if application.product.is_stamp_duty_applicable == False:
                        application.stamp_duty = 0
                    else:
                        branch=application.branch if application.branch else application.Originatedby.lm_branch_map.all().first()
                        if branch:
                            stamp_duty = application.branch.branch_stamp_duty.all().filter(query)

                            if len(stamp_duty) > 0:
                                s = stamp_duty[0]
                                if s.stamp_duty_percent:
                                    application.stamp_duty=float(s.stamp_duty_percent)*(application.loan_amount)/100
                                elif s.stamp_duty_amount:
                                    application.stamp_duty=float(s.stamp_duty_amount)
                        else:
                            application.stamp_duty=0

                    

                    

                    # if  (branch.stamp_duty_amount or branch.stamp_duty_percent) and branch.stamp_duty_minimum_amount_eligibility and application.loan_amount > branch.stamp_duty_minimum_amount_eligibility:
                    #     if branch.stamp_duty_amount:
                    #         application.stamp_duty=float(branch.stamp_duty_amount)
                    #     elif branch.stamp_duty_percent:
                    #         application.stamp_duty=float(branch.stamp_duty_percent)*(application.loan_amount)/100
                    # else:
                    #     application.stamp_duty=0
                    
                    
                    
                    # application.status = APPLICATION_STATUS.LOAN_AMOUNT_ADDED.value
                    # application.loan_amount=int(loan_amount)
                    # application.purpose_of_loan=purpose_of_loan
                    gold_rate_per_gram = helper.price_of_gold_22_karates()
                    # application.gold_rate_per_gram=float(gold_rate_per_gram['gold_price__avg'])
                    application.gold_rate_per_gram = gold_rate_per_gram
                    lendingGoldRate = gold_rate_per_gram * float(application.product.ltv_percentage / 100);
                    application.lending_gold_rate_per_gram = lendingGoldRate
                    
                    application.penalty=application.product.penalty
                    application.ltv=application.product.ltv_percentage
                    
                    application.tenure=application.product.tenure
                    application.intrest_rate=application.product.interest_rate
                    application.lender=application.product.lender
                    stamp_gst=application.stamp_duty if application.stamp_duty is not None else 0
                    disbursal_amount = float(application.loan_amount) - float(application.processing_fee) - float(application.gst) - stamp_gst
                    contraLoanNetPayableBalance=0
                    show_inspection_field=False
                    if application.application_type==ApplicationType.TAKEOVER.value and application.loan_amount>=int(environment.REQUEST_LOAN_AMOUNT_CHECK):
                        show_inspection_field=True

                    if application.product.contra_product is not None and contraLoanBaseAmount>0:
                        print('contra details added')
                        application.contra_loan_amount = contraLoanBaseAmount
                        # TO store
                        contraLoanPF = application.product.contra_product.processing_fee
                        contraLoanPFAmount = contraLoanBaseAmount * contraLoanPF / 100;
                        contraLoanGSTAmount = contraLoanPFAmount * 18 / 100;
                        contraLoanStampDutyAmount = 0
                        contraLoanNetPayableBalance = contraLoanBaseAmount - contraLoanPFAmount - contraLoanGSTAmount - contraLoanStampDutyAmount
                        application.contra_loan_processing_fee=contraLoanPF
                        application.contra_loan_processing_fee_amount=contraLoanPFAmount
                        application.contra_loan_gst_amount=contraLoanGSTAmount
                        application.contra_loan_stamp_duty_amount=contraLoanStampDutyAmount
                        application.contra_loan_net_payable_balance=contraLoanNetPayableBalance
                        print('contra net payable balance===========>', contraLoanNetPayableBalance)
                        #disbursal_amount += float(contraLoanNetPayableBalance)
                    print('disbursal amount', disbursal_amount)
                    print('contra net payable balance===========>', contraLoanNetPayableBalance)
                    print('contra net payable balance+ disbursal balanace===========>', float(contraLoanNetPayableBalance)+float(disbursal_amount))
                    previous_disbursal=ApplicationHelper().get_takeover_disbursal_amount(application_id=application.application_id)
                    print('previous disbursal', previous_disbursal)
                    print('contra net payable balance+ disbursal balanace - previous disbursal===========>',
                        float(contraLoanNetPayableBalance) + float(disbursal_amount)-float(previous_disbursal))
                    total_contra_gold_loan = disbursal_amount + float(contraLoanNetPayableBalance)
                    total_after_previous_disbursal = total_contra_gold_loan - float(previous_disbursal)
                    application.disbursal_amount = disbursal_amount

                    if application.application_type == 'TAKEOVER' and application.insurance_product:
                        print(total_after_previous_disbursal - float(application.insurance_amount_deducted))
                        net_payable = total_after_previous_disbursal - float(application.insurance_amount_deducted)
                        application.net_disbursed_amount = net_payable if net_payable > 0 else 0
                    else:
                        application.net_disbursed_amount = total_after_previous_disbursal
                    application.save()
                    print("insurance deduction after adding it", application.insurance_amount_deducted)
                    data=AddLoanAPISerializer(application).data
                    data['show_inspection_screen_loan_amount']=show_inspection_field
                    return HttpResponse.Success({"application":data})
                except Exception as e:
                    traceback.print_exc()
                    return HttpResponse.InternalServerError(str(e))
            
            elif user.role == ROLES.RELATIONSHIP_MANAGER.value:
                purpose_of_loan= request.data["purpose_of_loan"]
                allowed_purposes = [PurposeOfLoan.EXPANSION.value, PurposeOfLoan.STOCKS.value, PurposeOfLoan.CONSUMPTION.value, PurposeOfLoan.AGRI_ONLY.value]
                if purpose_of_loan not in allowed_purposes:
                    return HttpResponse.BadRequest("Invalid Choice")
                requested_loan_amount= request.data["requested_loan_amount"]
                expected_income_increase= request.data["expected_income_increase"]
                verify_the_usage= request.data["verify_the_usage"]
                application.status = APPLICATION_STATUS.LOAN_AMOUNT_ADDED.value
                application.purpose_of_loan=purpose_of_loan
                # TODO: Calculation 
                application.processing_fee=float(application.product.processing_fee)*(application.requested_loan_amount)/100
                application.current_gst_rate = float(environment.CURRENT_GTS_RATE)
                application.gst = (application.current_gst_rate/100) * application.processing_fee
                # application.application_loan_type = LENDING_TYPE.MSME_UNSECURED.value
                application.requested_loan_amount=requested_loan_amount
                application.expected_income_increase=expected_income_increase
                application.verify_the_usage=verify_the_usage
                branch=application.branch if application.branch else application.Originatedby.lm_branch_map.all().first()
                application.penalty=application.product.penalty
                application.tenure=application.product.tenure
                application.intrest_rate=application.product.interest_rate
                application.lender=application.product.lender
                application.net_disbursed_amount = 0
                application.save()
                data=AddRequestedAmountAPISerializer(application).data
                return HttpResponse.Success({"application":data})
            else:
                return HttpResponse.BadRequest("Only loan manager and relationship manager is allowed")
            
        except Application.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")
        except KeyError as e:
            return HttpResponse.BadRequest(f"Missing parameter: {e}")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
class GoodsView(APIView):
    def post(self,request):
        try:
        
            application=Application.objects.get(application_id=request.GET.get("application_id"," "))
            with transaction.atomic():
                goods_dict = request.data.get("goods", {})
                
                all_goods=WhiteGoods.objects.filter(goods_id__in=list(goods_dict.keys()))
                for good in goods_dict.keys():
                    obj=WhiteGoods.objects.get(goods_id=str(good))
                    customer_quantity=goods_dict[good]
                    # if obj.quantity_available==0:
                    #     return HttpResponse.BadRequest(f" {obj.goods_name} is out of stock.")
                    # if customer_quantity>obj.minimum_order_quantity:
                    #     return HttpResponse.BadRequest(f" quantity should be less than or equal to  {obj.minimum_order_quantity}.")
                    
                
                agm_objs_list = []
                total_goods_price = 0
                for each_goods in all_goods:
                    # print(each_goods.goods_id)
                    # print(goods_dict)
                    # print(goods_dict[each_goods.goods_id])
                    agm_objs_list.append(
                        ApplicationGoodsMapping(application=application, goods=each_goods, quantity=goods_dict[str(each_goods.goods_id)])
                    ) 
                    total_goods_price+=each_goods.goods_price * goods_dict[str(each_goods.goods_id)]

                # print("total_goods_price")
                # print(total_goods_price)

                
                if application.loan_amount<total_goods_price:
                    # TODO Show error
                    error_message = "Total Goods price(Rs."+str(total_goods_price)+") cannot exceed loan amount(Rs."+str(application.loan_amount)+")."
                    # FCMService([application.Originatedby]).generateNotification(
                    #                 title="Cannot add loan amount",
                    #                 message=error_message,
                    #             )
                    return HttpResponse.BadRequest(error_message)
                
                for good in goods_dict.keys():
                    obj=WhiteGoods.objects.get(goods_id=str(good))
                    customer_quantity=goods_dict[good]
                    obj.quantity_available=obj.quantity_available-customer_quantity
                    obj.save()
                
                # loan_amount = loan_amount-total_goods_price
                # net_disbursed_amount = loan_amount-total_goods_price
                # Delete old objects before creating new objects
                objects_to_delete = ApplicationGoodsMapping.objects.filter(application=application)
                objects_to_delete.delete()

                ajm_obj = ApplicationGoodsMapping.objects.bulk_create(agm_objs_list)

                application.total_goods_price=total_goods_price

                
                print(request.user)
                try:
                    # branch=BranchUserMapping.objects.get(user=request.user).branch
                    # print("branch.stamp_duty_amount:  ", branch.stamp_duty_amount)
                    # print("branch.stamp_duty_percent:  ", branch.stamp_duty_percent)
                    # print("branch.stamp_duty_minimum_amount_eligibility:  ", branch.stamp_duty_minimum_amount_eligibility)
                    # # branch=BranchProductMapping.objects.get(product_id=application.product,branch=loan_manager_branch).branch
                    # if  (branch.stamp_duty_amount or branch.stamp_duty_percent) and branch.stamp_duty_minimum_amount_eligibility and application.loan_amount >= branch.stamp_duty_minimum_amount_eligibility:
                    #     print("In first if")
                    #     if branch.stamp_duty_amount:
                    #         application.stamp_duty=float(branch.stamp_duty_amount)
                    #         print("In second if")
                    #     elif branch.stamp_duty_percent:
                    #         application.stamp_duty=float(branch.stamp_duty_percent)*(application.loan_amount)/100
                    #         print("In second elif")
                    #     else:
                    #         print("In thirs else")
                    #
                    # else:
                    #     print("In first else")
                    #     application.stamp_duty=0
                    # print('application net disbursed amount',application.net_disbursed_amount)
                    # print('goods price', total_goods_price)
                    # print('diff',application.net_disbursed_amount - total_goods_price)
                    print(application.net_disbursed_amount, total_goods_price)
                    application.net_disbursed_amount = application.net_disbursed_amount - total_goods_price
                    application.status=APPLICATION_STATUS.WHITE_GOODS_ADDED.value
                    application.save()
                except Exception as e:
                    traceback.print_exc()
                    print(e)

                
                # print("application.loan_amount: ", application.loan_amount)
                # print("application.processing_fee: ", application.processing_fee)
                # print("application.gst: ", application.gst)
                # print("application.stamp_duty: ", application.stamp_duty)

            return HttpResponse.Success({"application":AddGoodsAPISerializer(application).data})
            
        except Exception as e:
            traceback.print_exc()

        
    def get(self,request):
        try:
            application=Application.objects.get(application_id=request.GET.get("application_id"," "))
            disbursal_amount = float(application.loan_amount) - float(application.processing_fee) - float(application.gst) - float(application.stamp_duty)
            goods=WhiteGoods.objects.all()
            goods_li=[]
            for good in goods:
                if good.goods_price<=disbursal_amount:
                    goods_li.append(good)
            ser=WhiteGoodsSerializer(goods_li,many=True)
            return HttpResponse.Success({"goods":ser.data})

        except Exception as e:
            traceback.print_exc() 
            
        