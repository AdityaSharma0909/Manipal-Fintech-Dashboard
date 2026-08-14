from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from application.es_doc import ApplicationSearch
from application.es_doc import ApplicationSearchSerializer
from django.conf import settings
from utils.search import get_number_search_query, get_text_search_query

import traceback


class ApplicationSearchAPI(APIView):
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
                if 'application_number' in data:
                    query.append(get_text_search_query('application_number', data['application_number'])),
                if 'purpose_of_loan' in data:
                    query.append(get_text_search_query('purpose_of_loan', data['purpose_of_loan'])),
                if 'loan_amount' in data:
                    query.append(get_number_search_query('loan_amount', data['loan_amount'])),
                if 'contra_loan_amount' in data:
                    query.append(get_number_search_query('contra_loan_amount', data['contra_loan_amount'])),
                if 'application_type' in data:
                    query.append(get_text_search_query('application_type', data['application_type'])),
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

               
            # q = Q('bool',
            #     should=[Q('query', status=data['status']), Q('query', application_number=data['application_number'])],
            # )
            # apps = ApplicationSearch.search().filter("query_string", query={'account.customer_id':'RF272378056*'})
            # apps = ApplicationSearch.search().query("match", query={'account__customer_id':'RF272378056*'})
            # apps = ApplicationSearch.search().filter("match", status=data['status']).filter("query_string", query=data['application_number'])
            # a = ApplicationSearch.search().count()
            # apps = ApplicationSearch.search().index('applications').from_dict({
            q = {
                "from": offset,
                "size": page_limit,
                "query": {
                    "bool": {
                        "must": query
                    }
                }
            }
            apps = ApplicationSearch.search().from_dict(q).index('applications')
            # apps = a.filter('term', published=True)
            # print(q)

            # resp = []
            # print(":::: apps :::: ")
            # for app in apps:
            #     print(app)
            #     # d = ApplicationSearchSerializer(app).data
            #     print("\n")
            # print(":::: apps :::: ")
            # return HttpResponse.Success({"applications": resp})

            return HttpResponse.Success({"applications": ApplicationSearchSerializer(apps, many=True).data})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


