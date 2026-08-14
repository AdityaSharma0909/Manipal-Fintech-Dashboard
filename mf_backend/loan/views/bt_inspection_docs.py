from rest_framework.views import APIView

from loan.services.residence_takeover_details import TakeoverResidenceService
from utility.api_framework import ApiFramework


class BtInspectionDocView(APIView, ApiFramework):

    __data=None
    serializer=None
    response=None
    method=None
    __id=None

    def run_logic(self):
        service=TakeoverResidenceService()
        if self.method=="POST":
            self.response=service.add_docs(self.__data)
        elif self.method=="PATCH":
            self.response=service.update_docs(take_over_id=self.__id, data=self.__data)
        elif self.method=="DELETE":
            self.response=service.delete_docs(takeover_id=self.__id)
        else:
            self.response=service.get_data(take_over_residence_id=self.__id)

    def process(self):
        return self.response

    def post(self, request):
        self.method="POST"
        self.__data=request.data.copy()
        self.__data['account_id']=request.GET.get('account_id')
        return self.main()

    def patch(self, request):
        self.method="PATCH"
        self.__id=request.query_params.get('gprs_photos_id')
        self.__data=request.data
        return self.main()

    def get(self, request):
        self.method="GET"
        self.__id=request.query_params.get('take_over_residence_id')
        return self.main()
    def delete(self, request):
        self.method="DELETE"
        self.__id = request.query_params.get('gprs_photos_id')
        return self.main()