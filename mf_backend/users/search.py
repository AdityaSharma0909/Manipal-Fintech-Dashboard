from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from users.es_doc import UserSearch
from users.es_doc import UserSearchSerializer
from django.conf import settings
from utils.search import get_number_search_query, get_text_search_query

import traceback


class UserSearchAPI(APIView):
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
                if 'first_name' in data:
                    query.append(get_text_search_query('first_name', data['first_name'])),
                if 'last_name' in data:
                    query.append(get_text_search_query('last_name', data['last_name'])),
                if 'phone' in data:
                    query.append(get_text_search_query('phone', data['phone'])),
                if 'role' in data:
                    query.append(get_text_search_query('role', data['role'])),
                if 'designation' in data:
                    query.append(get_text_search_query('designation', data['designation'])),
                if 'aadhar_no' in data:
                    query.append(get_text_search_query('aadhar_no', data['aadhar_no'])),
                if 'pan_no' in data:
                    query.append(get_text_search_query('pan_no', data['pan_no'])),
                if 'employee_id' in data:
                    query.append(get_text_search_query('employee_id', data['employee_id'])),
                if 'date_of_joining' in data:
                    query.append(get_text_search_query('date_of_joining', data['date_of_joining'])),
                if 'email' in data:
                    query.append(get_text_search_query('email', data['email'])),
            
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
            users = UserSearch.search().from_dict(q).index('users')
            return HttpResponse.Success({"users": UserSearchSerializer(users, many=True).data})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


