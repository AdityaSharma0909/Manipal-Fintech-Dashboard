from django.db.models import Q
from rest_framework.views import APIView

from loan.models import Loan
from loan.service import LoanService
from loan.services.loan_payment_service import LoanPaymentService
from loan.serializers.loan_payment_serializer import LoanPaymentTransactionSerializer
from loan.services.loan_services import LoanHelper
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj


class LoanPaymentTransactionUtil(ApiFramework):

    def __init__(self, data, method, id=None, **kwargs):
        super().__init__(serializer_class=kwargs.get('serializer', None))
        self.__data = data
        self.__method = method
        self.__id = id
        self.__kwargs = kwargs
        self.__response = {}

    def format_request(self):
        pass

    def run_logic(self):
        service = LoanPaymentService(serializer=LoanPaymentTransactionSerializer, data=self.__data)
        if self.__method != "GET" and self.__id is None:
            self.__response=custom_response_obj(message='loan id is required', code=400)
        else:
            if self.__method == 'GET':
                loan_transaction_id=self.__kwargs.get('loan_payment_transaction_id', None)
                loan_id=self.__kwargs.get('loan_id', None)
                if loan_id is None and loan_transaction_id is None:
                    self.__response=custom_response_obj(message='loan id or loan payment transaction is required', code=400)
                elif loan_transaction_id is not None:
                    self.__response = service.get_data_by_id(loan_transaction_id)
                else:
                    self.__response = service.get_all_data(query=Q(**{'loan__loan_id':loan_id}))
            elif self.__method == 'POST':
                self.__data['loan']=self.__id
                self.__response = service.add_obj(data=self.__data,validate_add=True,validate_model=Loan, value=self.__id)
                LoanHelper().update_last_payment_transaction(loan_id=self.__id,payment_date=self.__data.get('payment_date'))
            elif self.__method == 'PATCH':
                self.__response = service.update_obj(self.__data,update_key_value=self.__id)
            elif self.__method == 'DELETE':
                self.__response = service.delete_obj(id=self.__id)

    def process(self):
        return self.__response


class LoanPaymentTransactionView(APIView):

    def get(self, request):
        loan_id = request.GET.get('loan_id', None)
        loan_transaction_id=request.GET.get('loan_payment_transaction_id', None)
        return LoanPaymentTransactionUtil(data=None, method='GET', loan_id=loan_id, loan_payment_transaction_id=loan_transaction_id).main()

    def post(self, request):
        data = request.data
        id = request.GET.get('loan_id', None)
        return LoanPaymentTransactionUtil(data=data, method='POST', id=id).main()

    def patch(self, request):
        data = request.data
        id=request.GET.get('loan_payment_transaction_id')
        return LoanPaymentTransactionUtil(data=data, method='PATCH', id=id).main()

    def delete(self, request):
        id=request.GET.get('loan_payment_transaction_id')
        return LoanPaymentTransactionUtil(data=None, method='DELETE', id=id).main()
