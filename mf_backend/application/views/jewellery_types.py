from rest_framework.views import APIView

from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj
from utils.constants import JewelleryItems


class JewelleryUtils(ApiFramework):


    def process(self):

        all_jewellry_list=[e.value for e in JewelleryItems]
        return custom_response_obj(message=all_jewellry_list, code=200)

class JewelleryView(APIView):

    def get(self, request):
        return JewelleryUtils().main()