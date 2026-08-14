from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from account.es_doc import AccountSearchSerializer, AccountSearch
from django.conf import settings
from utils.search import get_number_search_query, get_text_search_query

import traceback


class AccountSearchAPI(APIView):
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
                if 'customer_id' in data:
                    query.append(get_text_search_query('customer_id', data['customer_id'])),
                if 'email' in data:
                    query.append(get_text_search_query('email', data['email'])),
                if 'occupation' in data:
                    query.append(get_text_search_query('occupation', data['occupation'])),
                if 'sub_occupation' in data:
                    query.append(get_text_search_query('sub_occupation', data['sub_occupation'])),
                if 'net_annual_income' in data:
                    query.append(get_text_search_query('net_annual_income', data['net_annual_income'])),
                if 'aadhar_no' in data:
                    query.append(get_text_search_query('aadhar_no', data['aadhar_no'])),
                if 'pan_no' in data:
                    query.append(get_text_search_query('pan_no', data['pan_no'])),
            
            q = {
                "from": offset,
                "size": page_limit,
                "query": {
                    "bool": {
                        "must": query
                    }
                }
            }
            accounts = AccountSearch.search().from_dict(q).index('accounts')
            return HttpResponse.Success({"customers": AccountSearchSerializer(accounts, many=True).data})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


