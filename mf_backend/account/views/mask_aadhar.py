from rest_framework.views import APIView

from account.service.aadhar_mask import AadharMask
from utility.api_framework import ApiFramework


class MaskAadhar(ApiFramework):

    def __init__(self, data):
        super().__init__()
        self.__data=data

    def process(self):
        masked_file=AadharMask().mask_aadhar(self.__data)

class MaskAadharView(APIView):

    def post(self, request):
        data=request.data
        return MaskAadhar(data=data).main()