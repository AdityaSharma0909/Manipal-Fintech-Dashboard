from rest_framework.views import APIView
from document.utils.asset_document_utils import AssetDocumentUtils
from document.serializers import AssetDocumentSerializer
from utils.responseHandler import HttpResponse
from asset.models import Asset ,GoldAppriaselModel
from application.models import Application 
import traceback
from document.utils import asset_document_utils
from account.models import Account
from ..serializers import (
    AssetSerializer,
    AssetSingleSerializer,
    AssetSerializerModified,GoldAppriaselSerializer,GoldAppriaselCreateSerializer
)
from instance import SerilizerInstance
import utils.helper as helper
from utils.constants import APPLICATION_STATUS


class GoldAppriaselView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            asset = Asset.objects.get(
                asset_id=request.GET.get("asset_id", "")
            )
            data["asset"]=asset.asset_id
            data["appriased_by"]=request.user.user_id
            ser=GoldAppriaselCreateSerializer(data=data)
            if ser.is_valid():
                ser.save()
                return HttpResponse.Success(ser.data)
            return HttpResponse.InternalServerError(ser.errors)
            
            
        except Exception as e:
            traceback.print_exc()
    
    def get(self, request, *args, **kwargs):
        try:
           
            goldappriasel = GoldAppriaselModel.objects.get(
                goldappriase_id=request.GET.get("goldappriase_id", "")
            )
            ser=GoldAppriaselSerializer(goldappriasel)
            return HttpResponse.Success(ser.data)
        except Exception as e:
            traceback.print_exc()
    
    def patch(self, request, *args, **kwargs):
        try:
            data = request.data
            goldappriasel = GoldAppriaselModel.objects.get(
                goldappriase_id=request.GET.get("goldappriase_id", "")
            )
            ser=GoldAppriaselCreateSerializer(goldappriasel,data=data,partial=True)
            if ser.is_valid():
                ser.save()
                return HttpResponse.Success(ser.data)
            return HttpResponse.InternalServerError(ser.errors)
            
        except Exception as e:
            traceback.print_exc()


