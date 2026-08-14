from django.db.models import Q
from rest_framework.views import APIView
from loan.services.residence_takeover_details import TakeoverResidenceService
from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj


class LoanTakeOverResidenceUtil(ApiFramework):

    def __init__(self, data, method, user, id=None, **kwargs):
        super().__init__()
        self.__data = data
        self.__method = method
        self.__id = id
        self.__kwargs = kwargs
        self.__response = {}
        self.__application_id=kwargs.get('application_id', None)
        self.__orginated_by=user
        self.__service = TakeoverResidenceService()

    def run_logic(self):
        if (self.__method=="POST" or self.__method=="GET") and self.__application_id is None:
            self.__response=custom_response_obj(message={'msg':'application id is required'}, code=400)
        elif self.__method != "POST" and self.__id is None:
            self.__response=custom_response_obj(message={'msg':'take over residence details id is required'}, code=400)
        else:
            if self.__method == 'GET':
                self.__response=self.__service.get_account_details(account_id=self.__id,
                                                                   application=self.__application_id)
            elif self.__method == 'POST':
                self.__response=self.__service.add_takeover_residence(self.__data, application_id=self.__application_id)
            elif self.__method == 'PATCH':
                self.__response=self.__service.update_details(self.__data,
                                                              takeover_residence_id=self.__id,
                                                              application_id=self.__application_id)
            else:
                self.__response = self.__service.delete_details(takeover_residence_id=self.__id)

    def process(self):
        return self.__response


class LoanTakeOverResidenceView(APIView):

    def get(self, request):
        take_over_id=request.query_params.get('account_id')
        application_id=request.query_params.get('application_id')
        return LoanTakeOverResidenceUtil(data=None, method='GET', user=None,
                                         id=take_over_id, application_id=application_id).main()

    def post(self, request):
        data = request.data
        application_id=request.query_params.get('application_id', None)
        return LoanTakeOverResidenceUtil(data=data, method='POST', user=request.user.user_id,
                                         application_id=application_id).main()

    def patch(self, request):
        data = request.data
        id=request.query_params.get('take_over_residence_details_id')
        application_id=request.query_params.get('application_id')
        return LoanTakeOverResidenceUtil(data=data, method='PATCH', id=id, user=request.user.user_id,
                                         application_id=application_id).main()

    def delete(self, request):
        id = request.query_params.get('take_over_residence_details_id')
        return LoanTakeOverResidenceUtil(data=None, method='DELETE', id=id, user=request.user.user_id).main()