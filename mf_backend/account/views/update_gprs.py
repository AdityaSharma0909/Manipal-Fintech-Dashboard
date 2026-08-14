from rest_framework.response import Response
from rest_framework.views import APIView

from account.service.accountService import AccountService
from utility.api_framework import ApiFramework


class UpdateGprsDataView(APIView, ApiFramework):

    response={}
    method=""
    serializer=None
    service=AccountService()
    __data=None
    def run_logic(self):
        if self.method=="PATCH":
            self.response=self.service.change_status(self.__data)
        elif self.method=="POST":
            # self.response=self.service.upload_gprs_photo(self.__data)
            data = self.__data.get('data')
            account_id = self.__data.get('account_id')
            application_id = self.__data.get('application_id')
            user = self.__data.get('user')
            self.response=self.service.upload_gprs_photo(data,account_id=account_id, application_id=application_id, user=user)
        elif self.method=="DELETE":
            self.response=self.service.delete_gprs_photo(self.__data)
        # elif self.method=='GET':
        #     self.response=self.service.get_gprs_photos(self.__data)
        elif self.method == 'GET':
            # Unpack user and account_id from __data
            account_id = self.__data.get('account_id')
            application_id = self.__data.get('application_id')
            user = self.__data.get('user')
            self.response = self.service.get_gprs_photos(account_id=account_id, application_id=application_id, user=user)

    def process(self):
        return self.response

    def patch(self, request):
        self.__data=request.data.get('account_id', None)
        if self.__data is None:
            return Response(data={'msg':'account_id is required'}, status=200)
        self.method="PATCH"
        return self.main()

    def post(self, request):
        # self.__data=request.data
        data = request.data
        account_id = request.GET.get('account_id', None)
        if account_id is None:
            return Response(data={'msg': 'account_id is required'}, status=200)
        application_id = request.GET.get('application_id', None)
        self.__data = {
            'data':data,
            'account_id': account_id,
            'application_id':application_id,
            'user': request.user
            
        }
        self.__data['account'] = account_id
        self.__data['application'] = application_id
        self.method="POST"
        return self.main()


    def delete(self, request):
        self.__data=request.data.get('gprs_photo_id')
        self.method="DELETE"
        return self.main()


    # def get(self, request):
    #     self.__data = request.GET.get('account_id', None)
    #     if self.__data is None:
    #         return Response(data={'msg': 'account_id is required'}, status=200)
    #     self.method = "GET"
    #     return self.main()

    def get(self, request):
        account_id = request.GET.get('account_id', None)
        if account_id is None:
            return Response(data={'msg': 'account_id is required'}, status=200)
        application_id = request.GET.get('application_id', None)
        # Include account_id and user in self.__data
        self.__data = {
            'account_id': account_id,
            'application_id':application_id,
            'user': request.user
        }
        self.method = "GET"
        return self.main()
        