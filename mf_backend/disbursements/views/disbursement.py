import datetime
import time

from django.db.models import Value, F, DateTimeField
from django.db.models.functions import Concat, Trunc, Extract
from rest_framework.views import APIView
from utility.api_framework import ApiFramework
from ..serializers import DisbursementSerializer
from utils.responseHandler import HttpResponse
import traceback
from ..models import Disbursement
from ..service.dibursements_service import DisbursementHelper




class DisburseUtl(ApiFramework):

    def __init__(self, data, user, method):
        super().__init__()
        self.__data=data
        self.__user=user
        self.__method=method
        self.__response={}


    def format_request(self):
        pass

    def run_logic(self):
        service=DisbursementHelper()
        if self.__method=='POST':
            self.__response=service.disburse_loan(data=self.__data, user=self.__user)
            print(self.__response)

    def process(self):
        return self.__response


class DisbursementView(APIView):

    def post(self, request):
        data=request.data

        return DisburseUtl(data=data, user=request.user, method='POST').main()


    def patch(self, request):
        try:
            data = request.data
            disbursment = Disbursement.objects.get(disbursement_id=request.GET.get("disbursement_id", ""))
            utr=data.get('utr_no', None)
            if utr:
                # if disbursment.utr_no is not None:
                #     return HttpResponse.Forbidden({'error':'Disbursement already has a utr no'})
                disbursment.payment_mode=data.get('payment_mode', disbursment.payment_mode)
                disbursment.utr_no=utr
                disbursment.save()
                return HttpResponse.Success({"disbursment": DisbursementSerializer(disbursment).data})
            serializer = DisbursementSerializer(disbursment, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"disbursment": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except Disbursement.DoesNotExist as e:
            return HttpResponse.BadRequest(e)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    #get loan by loan id
    def get(self, request):
        try:
            disbursment = Disbursement.objects.get(disbursement_id=request.GET.get("disbursement_id", ""))

            serializer = DisbursementSerializer(disbursment)
            # print(lead.phone)

            # account=Account.objects.get(user__in=User.objects.filter(phone=lead.phone))

            # print(account)

            return HttpResponse.Success({"disbursment": serializer.data})
        except Disbursement.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class DisbursementAllView(APIView):
    def get(self, request):
        try:
            filters=request.query_params
            if len(filters)>0:
                data=DisbursementHelper().get_pending_disbursals(filters)
                return HttpResponse.Success({"disbursements": data})
            else:
                data = list(Disbursement.objects.all().values('utr_no',"disbursement_id",
                                                                        'payment_mode',
                                                                        'disbursal_date',
                                                                        'disbursement_status',
                                                                        'disbursement_amount',
                                                                        'payment_status',

                                                                           ).annotate(
                    application_number=F('application__application_number'),
                    application_id=F('application__application_id'),
                    loan_id=F('loan__loan_id'),
                    loan_amount=F('loan__loan_amount'),
                    loan_number=F('loan__loan_number'),
                    name=Concat(F('application__account__user__first_name'), Value(' '),
                                F('application__account__user__last_name')),
                    created_at=F('created_at'),
                    modified_at=F('modified_at'),
                ).order_by('-modified_at'))
                return HttpResponse.Success({"disbursements": data})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
