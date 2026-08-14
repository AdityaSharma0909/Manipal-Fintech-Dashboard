from rest_framework.views import APIView
from asset.services.gold_price_service_v2 import GoldPriceServiceV2
from utility.api_framework import ApiFramework


class GoldPriceV2Util(ApiFramework):

    def __init__(self, data, method):
        super().__init__()
        self.__data=data
        self.__method=method

    def process(self):
        service=GoldPriceServiceV2()
        if self.__method=='GET':
            return service.get_price()
        # if self.__method=='PATCH':
        #     return service.update_data(data=self.__data, id=self.__data.get('karat'))
        if self.__method=='POST':
            return service.add_data(data=self.__data)

class GoldPriceV2View(APIView):

    def get(self, request):
        return GoldPriceV2Util(data=None, method='GET').main()

    def post(self, request):
        data=request.data
        return GoldPriceV2Util(data=data, method='POST').main()
