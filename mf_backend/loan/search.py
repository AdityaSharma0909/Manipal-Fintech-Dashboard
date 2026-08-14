from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from loan.es_doc import LoanSearch
from loan.es_doc import LoanSearchSerializer
from django.conf import settings
from utils.search import get_number_search_query, get_text_search_query

import traceback


class LoanSearchAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            query = []

            pg = request.GET.get('pg', None)
            page_no = 1
            offset = 0
            page_limit = int(settings.API_PAGE_SIZE)
            if pg is not None:
                try:
                    page_no = int(pg)
                    offset = (page_no - 1) * page_limit
                except ValueError as ve:
                    return HttpResponse.BadRequest("Please send correct 'pg' param.")
            
            if '*' in data:
                query.append(get_text_search_query('*', data['*']))
            else:
                if 'status' in data:
                    query.append(get_text_search_query('status', data['status'])),
                if 'loan_number' in data:
                    query.append(get_text_search_query('loan_number', data['loan_number'])),
                if 'purpose_of_loan' in data:
                    query.append(get_text_search_query('purpose_of_loan', data['purpose_of_loan'])),
                if 'loan_amount' in data:
                    query.append(get_number_search_query('loan_amount', data['loan_amount'])),
                if 'tenure' in data:
                    query.append(get_number_search_query('tenure', data['tenure'])),
                if 'loan_type' in data:
                    query.append(get_text_search_query('loan_type', data['loan_type'])),
                if 'disbursal_amount' in data:
                    query.append(get_number_search_query('disbursal_amount', data['disbursal_amount'])),
                if 'account.customer_id' in data:
                    query.append(get_text_search_query('account.customer_id', data['account.customer_id'])),
                if 'account.email' in data:
                    query.append(get_text_search_query('account.email', data['account.email'])),
                if 'account.occupation' in data:
                    query.append(get_text_search_query('account.occupation', data['account.occupation'])),
                if 'account.net_annual_income' in data:
                    query.append(get_number_search_query('account.net_annual_income', data['account.net_annual_income'])),
                if 'account.aadhar_no' in data:
                    query.append(get_text_search_query('account.aadhar_no', data['account.aadhar_no'])),
                if 'account.pan_no' in data:
                    query.append(get_text_search_query('account.pan_no', data['account.pan_no'])),
                if 'account.first_name' in data:
                    query.append(get_text_search_query('account.first_name', data['account.first_name'])),
                if 'account.last_name' in data:
                    query.append(get_text_search_query('account.last_name', data['account.last_name'])),
                if 'branch.branch_name' in data:
                    query.append(get_text_search_query('branch.branch_name', data['branch.branch_name'])),
                if 'branch.branch_code' in data:
                    query.append(get_text_search_query('branch.branch_code', data['branch.branch_code'])),
            q = {
                "from": offset,
                "size": page_limit,
                "query": {
                    "bool": {
                        "must": query
                    }
                }
            }
            loans = LoanSearch.search().from_dict(q).index('loans')
            return HttpResponse.Success({"loans": LoanSearchSerializer(loans, many=True).data})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


