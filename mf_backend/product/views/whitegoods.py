from rest_framework.views import APIView
from ..serializers import WhiteGoodsSerializer ,ProductWhiteGoodsMappingSerializer
from utils.responseHandler import HttpResponse
from product.models import Product,WhiteGoods ,ProductWhiteGoodsMapping
from rest_framework.permissions import AllowAny
from users.models import User
from utils.constants import ROLES

import traceback


class WhiteGoodsView(APIView):

    def get(self,request):
        try:
            if request.GET.get("product_id", ""):
                # get goods by product id
                 
                product = Product.objects.get(product_id=request.GET.get("product_id", ""))
                data=ProductWhiteGoodsMapping.objects.filter(product=product)
                ser=ProductWhiteGoodsMappingSerializer(data,many=True)
                return HttpResponse.Success({"whitegoods":ser.data})
            elif request.GET.get("goods_id", ""):
                # get single goods by goods id
                goods = WhiteGoods.objects.get(goods_id=request.GET.get("goods_id", ""))
                ser=WhiteGoodsSerializer(goods)
                return HttpResponse.Success({"whitegoods":ser.data})
            else:
                role=request.user.role
                if role in [ROLES.CPC.value,ROLES.BUSINESS_HEAD.value,ROLES.CLUSTER_MANAGER.value,
                            ROLES.CHIEF_BUSINESS_OPERATOR.value,ROLES.REGIONAL_HEAD.value,
                            ROLES.BRANCH_MANAGER.value, ROLES.BRANCH_OPERATION_MANAGER.value]:
                    goods=WhiteGoods.objects.all()
                    ser=WhiteGoodsSerializer(goods,many=True)
                else:
                    lm_state=request.user.lm_branch_map.all().first().branch.state
                    goods=WhiteGoods.objects.filter(available_in__icontains=lm_state)
                    ser=WhiteGoodsSerializer(goods,many=True)
                return HttpResponse.Success({"whitegoods":ser.data})
        except Product.DoesNotExist as e:
            return HttpResponse.BadRequest(e)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
    


    def post(self,request):
            # goods = WhiteGoods.objects.get(goods_id=request.GET.get("goods_id", ""))
            # application=Application.objects.get(application_id=request.GET.get("application_id", ""))
            # application.goods=goods
            # application.save()
            # data["status"]=constants.APPLICATION_STATUS.NEW_APPLICATION.value

            data=request.data
            data["created_by"]=request.user.user_id
            ser=WhiteGoodsSerializer(data=data)
            if ser.is_valid():
                ser.save()
                return HttpResponse.Success({"whitegoods":ser.data})
            
            return HttpResponse.BadRequest({'error':ser.errors  } )
        
    def patch(self,request):
        try:
            data = request.data
            goods_id = request.GET.get("goods_id", "")
            whiteGood = WhiteGoods.objects.get(goods_id=goods_id)
            serializer = WhiteGoodsSerializer(whiteGood,data=data,partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"good": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except WhiteGoods.DoesNotExist as e:
             return HttpResponse.BadRequest(e)
        except Exception as e:
             traceback.print_exc()
             return HttpResponse.InternalServerError(str(e))
        
        
        
            

# TODO: remove this view in production just using it to add white goods in system
class WhiteGoodsTestView(APIView):

    permission_classes = (AllowAny,)

    def post(self,request):
            data=request.data
            for d in data:
                d["created_by"]=str(User.objects.get(username='admin').user_id)
                ser=WhiteGoodsSerializer(data=d)
                if ser.is_valid():
                    ser.save()

            return HttpResponse.Success({})
            
        