from django.db.models import Q
from rest_framework.views import APIView

from application.models import Application
from branch.models import Branch
from ..serializers import ProductSerializer ,ProductSpecificDocumentsSerializer ,ProductCreateSerializer
from utils.responseHandler import HttpResponse
from product.models import Product ,ProductSpecificDocuments
import traceback
from rest_framework.permissions import AllowAny
from utils.constants import LOAN_TYPE, ROLES
from rest_framework.pagination import PageNumberPagination


class ProductView(APIView , PageNumberPagination):
    #post single product
    def post(self,request, *args):
        try :
            data=request.data

            # data["lender"]=Lender.objects.get(lender_id=str(data["lender"]))

            ser=ProductCreateSerializer(data=data)
            if ser.is_valid():
                
                ser.save()
                product=Product.objects.get(product_id=ser.data["product_id"])
                # if ser.data["has_white_goods"]==True:                
                    
                #     for goods in data["goods"]:
                #         good=WhiteGoods.objects.get(goods_id=str(goods))
                #         ProductWhiteGoodsMapping.objects.create(product=product,goods=good,created_by=request.user).save()
                #         # WhiteGoods.objects.create(**goods).save()
                        
                if 'documents' in data and data["documents"] != None:
                    for doc in data["documents"]:
                        
                        document_name=doc["document_name"]
                        document_description=doc["document_description"]
                        document_type=document_name.upper().replace(" ","_")+"_TYPE"
                        is_required=doc["is_required"]
                        ProductSpecificDocuments.objects.create(document_name=document_name,document_description=document_description,document_type=document_type,is_required=is_required,product=product,created_by=request.user).save()       
                
                return HttpResponse.Success({"product":ser.data})
            return HttpResponse.BadRequest({"error":ser.errors})

            
        except Product.DoesNotExist as e:
            return HttpResponse.BadRequest(e)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
    
    #get all products
    # def get(self, request, *args, **kwargs):

    #     query_options={}

    #     application_id=request.GET.get('application_id',None)
    #     print(application_id)
    #     try :
    #         user_role=request.user.role
    #         if application_id:
    #             application = Application.objects.get(application_id=application_id)
    #             query_options['lender__lender_code'] = application.lender.lender_code
    #         if user_role==ROLES.LOAN_OFFICER.value:

    #             query_options['product_type']=LOAN_TYPE.GOLD_LOAN.value
    #             query_options['active'] = True

    #         #filter change start

                
    #             active = request.GET.get('active', None)
    #             if active is not None:
    #                 query_options['active__in'] = active.split(",")

    #             lender = request.GET.get('lender', None)
    #             if lender is not None:
    #                 lender_list = lender.split(",")
    #                 query_options['lender__in'] = lender_list
    #             data=Product.objects.filter(Q(**query_options))
    #         #filter change end
            
    #         else:
    #             query_filters = request.query_params
    #             if query_filters:
    #                 options = ['product_name', 'product_category', 'minimum_ticket_size', 'maximum_ticket_size',
    #                            'maximum_ticket_size__lte', 'maximum_ticket_size__gte',
    #                            'minimum_ticket_size__lte', 'minimum_ticket_size__gte', 'lender__lender_name',
    #                            'lender_name']
    #                 for i in options:
    #                     key=i
    #                     if i == 'lender_name':
    #                         key='lender__lender_name'
    #                     temp = query_filters.get(i)

    #                     if temp is not None:
    #                         query_options[key] = query_filters.get(i)

    #             query_options['product_type']=LOAN_TYPE.GOLD_LOAN.value
    #             print('query_options=====>',query_options)
    #             data=Product.objects.filter(Q(**query_options)).order_by('-modefied_at')
    #         #pagination changes start
    #         paginated_data=self.paginate_queryset(data, request)
    #         resp = ProductSerializer(paginated_data,many=True).data
    #         resp=self.get_paginated_response(resp).data
    #         resp['product']=resp.pop('results')
    #         return HttpResponse.Success(resp)
    #         #pagination changes end
    #         # ser=ProductSerializer(data,many=True) //This exists in Existing code
            
    #         # return HttpResponse.Success({"product":ser.data}) //This exists in Existing code
    #     except Application.DoesNotExist as e:
    #         return HttpResponse.BadRequest(e)
    #     except Product.DoesNotExist as e:
    #         return HttpResponse.BadRequest(e)
    #     except Exception as e:
    #         traceback.print_exc()
    #         return HttpResponse.InternalServerError(str(e))
    
    # def get(self, request, *args, **kwargs):
    #     query_options = {}

    #     application_id = request.GET.get('application_id', None)
    #     try:
    #         user_role = request.user.role
    #         user = request.user
    #         if application_id:
    #             application = Application.objects.get(application_id=application_id)
    #             query_options['lender__lender_code'] = application.lender.lender_code

    #         if user_role in [ROLES.LOAN_OFFICER.value , ROLES.BRANCH_MANAGER.value]:
    #             query_options['product_type__in'] = [ LOAN_TYPE.GOLD_LOAN.value , LOAN_TYPE.WELLNESS.value ]
    #             query_options['active'] = True

    #         elif user_role in [ROLES.RELATIONSHIP_MANAGER.value , ROLES.CREDIT_MANAGER.value]:
    #             query_options['product_type__in'] = [ LOAN_TYPE.MSME_UNSECURED.value , LOAN_TYPE.WELLNESS.value ]

    #         # Apply filter for all roles
    #         else:
    #             apply_filter(request, query_options)
    #             query_filters = request.query_params
    #             if query_filters:
    #                 options = ['product_name', 'product_category', 'minimum_ticket_size', 'maximum_ticket_size',
    #                         'maximum_ticket_size__lte', 'maximum_ticket_size__gte',
    #                         'minimum_ticket_size__lte', 'minimum_ticket_size__gte', 'lender__lender_name',
    #                         'lender_name']
    #                 for i in options:
    #                     key = i
    #                     if i == 'lender_name':
    #                         key = 'lender__lender_name'
    #                     temp = query_filters.get(i)

    #                 if temp is not None:
    #                     query_options[key] = query_filters.get(i)

    #             query_options['product_type__in'] = [LOAN_TYPE.GOLD_LOAN.value, LOAN_TYPE.MSME_UNSECURED.value , LOAN_TYPE.WELLNESS.value]
                
    #         data = Product.objects.filter(Q(**query_options)) #.order_by('-modefied_at')
    #         print("Product filter: ", query_options)

    #         # paginated_data = self.paginate_queryset(data, request)
    #         # resp = ProductSerializer(paginated_data, many=True).data
    #         # resp = self.get_paginated_response(resp).data
    #         # resp['product'] = resp.pop('results')

    #         resp = ProductSerializer(data, many=True).data
    #         return HttpResponse.Success({'product': resp})
    #     except Application.DoesNotExist:
    #         return HttpResponse.NotFound("Application not found")
    #     except Product.DoesNotExist:
    #         return HttpResponse.NotFound("Product not found")
    #     except Exception as e:
    #         return HttpResponse.InternalServerError(str(e))

    def get(self, request, *args, **kwargs):
        query_options = {}

        application_id = request.GET.get('application_id', None)
        try:
            user = request.user
            user_role = user.role  # Assuming `role` is stored in `role` field
            
            if application_id:
                application = Application.objects.get(application_id=application_id)
                query_options['lender__lender_code'] = application.lender.lender_code

            # Role-based filtering
            if user_role in [ROLES.LOAN_OFFICER.value, ROLES.BRANCH_MANAGER.value]:
                query_options['product_type__in'] = [LOAN_TYPE.GOLD_LOAN.value, LOAN_TYPE.WELLNESS.value]
                query_options['active'] = True

            elif user_role in [ROLES.RELATIONSHIP_MANAGER.value, ROLES.CREDIT_MANAGER.value]:
                query_options['product_type__in'] = [LOAN_TYPE.MSME_UNSECURED.value, LOAN_TYPE.MSME_UNSECURED_AGRI.value, LOAN_TYPE.WELLNESS.value]

            # Apply filter for all roles
            else:
                apply_filter(request, query_options)
                query_filters = request.query_params
                if query_filters:
                    options = ['product_name', 'product_category', 'minimum_ticket_size', 'maximum_ticket_size',
                            'maximum_ticket_size__lte', 'maximum_ticket_size__gte', 'minimum_ticket_size__lte',
                            'minimum_ticket_size__gte', 'lender__lender_name', 'lender_name']
                    for i in options:
                        key = i
                        if i == 'lender_name':
                            key = 'lender__lender_name'
                        temp = query_filters.get(i)
                        if temp is not None:
                            query_options[key] = temp

                    query_options['product_type__in'] = [LOAN_TYPE.GOLD_LOAN.value, LOAN_TYPE.MSME_UNSECURED.value, LOAN_TYPE.WELLNESS.value , LOAN_TYPE.MSME_UNSECURED_AGRI.value]

            # Check if `is_available_to_all_branches` is True
            if 'is_available_to_all_branches' not in query_options:
                # If `is_available_to_all_branches` is True, show all products
                query_options['is_available_to_all_branches'] = True

            # Otherwise, filter based on the user's branches if available_in_branches is False
            else:
                user_branches = user.lm_branch_map.all()  # Get all branches mapped to the user
                query_options['available_in_branches__in'] = user_branches

            # Filter products based on the query options
            data = Product.objects.filter(Q(**query_options))  # .order_by('-modefied_at')

            print("Product filter: ", query_options)

            # paginated_data = self.paginate_queryset(data, request)
            # resp = ProductSerializer(paginated_data, many=True).data
            # resp = self.get_paginated_response(resp).data
            # resp['product'] = resp.pop('results')

            resp = ProductSerializer(data, many=True).data
            return HttpResponse.Success({'product': resp})

        except Application.DoesNotExist:
            return HttpResponse.NotFound("Application not found")
        except Product.DoesNotExist:
            return HttpResponse.NotFound("Product not found")
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
    
    def patch(self, request):
        try:
            data = request.data
            product = Product.objects.get(product_id=request.GET.get("product_id", ""))
            serializer = ProductCreateSerializer(product, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                product=Product.objects.get(product_id=serializer.data["product_id"])
                # if serializer.data["has_white_goods"]==True:                
                    
                #     for goods in data["goods"]:
                #         good=WhiteGoods.objects.get(goods_id=str(goods))
                #         ProductWhiteGoodsMapping.objects.create(product=product,goods=good,created_by=request.user).save()
                #         # WhiteGoods.objects.create(**goods).save()
                        
                if len(data["documents"])> 0:
                    for doc in data["documents"]:
                        product_id=doc.get("product_document_id", None)
                        if product_id is not None:
                            document = ProductSpecificDocuments.objects.get(product_document_id=doc.get("product_document_id"))
                            print(document)
                            print(doc)
                            document_ser = ProductSpecificDocumentsSerializer(document,data=doc,partial=True)
                            print(document_ser)
                            if document_ser.is_valid():
                                document_ser.save()
                
                # if serializer.data["has_white_goods"]==True:

                #     for goods in data["goods"]:
                        
                #         goods["product"]=product
                #         goods["created_by"]=request.user

                #         WhiteGoods.objects.create(**goods).save()
                        
                # if serializer.data["has_required_documents"]==True:
                #     for doc in data["documents"]:
                #         doc["product"]=product
                #         doc["created_by"]=request.user
                #         ProductSpecificDocuments.objects.create(**doc).save()     
                return HttpResponse.Success({"product": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except Product.DoesNotExist as e:
            return HttpResponse.BadRequest(e)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
class SingleProductView(APIView):
    #get single product
    def get(self,request, *args, **kwargs):
        try :
            product = Product.objects.get(product_id=request.GET.get("product_id", ""))
            ser=ProductSerializer(product)
            return HttpResponse.Success({"product":ser.data})
        except Product.DoesNotExist as e:
            return HttpResponse.BadRequest(e)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
    
   

# TODO: remove this view in production just using it to add products in system
class ProductTestView(APIView):
    
    permission_classes = (AllowAny,)

    def post(self,request, *args):
        try :
            data=request.data
            resp = {
                "errors": []
            }
            for d in data:
                ser=ProductCreateSerializer(data=d)
                if ser.is_valid():
                    
                    ser.save()
                    product=Product.objects.get(product_id=ser.data["product_id"])
                    # if ser.data["has_white_goods"]==True:                
                        
                    #     for goods in data["goods"]:
                    #         good=WhiteGoods.objects.get(goods_id=str(goods))
                    #         ProductWhiteGoodsMapping.objects.create(product=product,goods=good,created_by=request.user).save()
                    #         # WhiteGoods.objects.create(**goods).save()
                            
                    if d["documents"] != None:
                        for doc in d["documents"]:
                            
                            document_name=doc["document_name"]
                            document_description=doc["document_description"]
                            document_type=document_name.upper().replace(" ","_")+"_TYPE"
                            is_required=doc["is_required"]
                            ProductSpecificDocuments.objects.create(document_name=document_name,document_description=document_description,document_type=document_type,is_required=is_required,product=product,created_by=request.user).save()       
                
                    resp[ser.data["product_id"]] = ser.data
                else:
                    resp["errors"].append(ser.errors)

            return HttpResponse.Success(resp)
            
        except Product.DoesNotExist as e:
            return HttpResponse.BadRequest(e)
        except Exception as e:
            traceback.print_exc()

def apply_filter(request, query_options):
    active = request.GET.get('active', None)
    if active is not None:
        query_options['active__in'] = active.split(",")

    lender = request.GET.get('lender', None)
    if lender is not None:
        lender_list = lender.split(",")
        query_options['lender__in'] = lender_list