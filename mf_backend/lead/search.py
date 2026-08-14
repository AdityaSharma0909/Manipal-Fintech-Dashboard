from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from lead.es_doc import LeadSearch
from lead.es_doc import LeadSearchSerializer
from django.conf import settings
from utils.search import get_number_search_query, get_text_search_query


import traceback


def get_search_query(key, value):
    return {
        "query_string": {
            "query": f"{key}:{value}*"
        }
    }

class LeadSearchAPI(APIView):
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
                    query.append(get_search_query('status', data['status'])),
                if 'first_name' in data:
                    query.append(get_search_query('first_name', data['first_name'])),
                if 'last_name' in data:
                    query.append(get_search_query('last_name', data['last_name'])),
                if 'lead_type' in data:
                    query.append(get_search_query('lead_type', data['lead_type'])),
                if 'phone' in data:
                    query.append(get_search_query('phone', data['phone'])),
                if 'account.customer_id' in data:
                    query.append(get_search_query('account.customer_id', data['account.customer_id'])),
                if 'account.email' in data:
                    query.append(get_search_query('account.email', data['account.email'])),
                if 'account.occupation' in data:
                    query.append(get_search_query('account.occupation', data['account.occupation'])),
                if 'account.net_annual_income' in data:
                    query.append(get_search_query('account.net_annual_income', data['account.net_annual_income'])),
                if 'account.aadhar_no' in data:
                    query.append(get_search_query('account.aadhar_no', data['account.aadhar_no'])),
                if 'account.pan_no' in data:
                    query.append(get_search_query('account.pan_no', data['account.pan_no'])),
                
               
            # q = Q('bool',
            #     should=[Q('query', status=data['status']), Q('query', application_number=data['application_number'])],
            # )
            # apps = ApplicationSearch.search().filter("match", status=data['status']).filter("query_string", query=data['application_number'])
            q = {
                "from": offset,
                "size": page_limit,
                "query": {
                    "bool": {
                        "must": query
                    }
                }
            }
            leads = LeadSearch.search().from_dict(q).index('leads')
            return HttpResponse.Success({"leads": LeadSearchSerializer(leads, many=True).data})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


