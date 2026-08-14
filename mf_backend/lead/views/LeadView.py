from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers import LeadDisplaySerializer, LeadCreateSerializer, LeadResponseSerializer 
from document.serializers import LeadDocumentSerializer
from utils.responseHandler import HttpResponse
from ..models import Lead , LeadDocument
from utils.constants import ROLES, LEAD_STATUS, LENDER , LENDING_TYPE , LEAD_DOCUMENT
import traceback
from lender.models import Lender
from branch.models import Branch, BranchUserMapping
from utility.response_handler import HttpResponse as resp
from ..services.axis_bank_apis import AxisBankCalls
from ..services.lead_services import LeadService
from datetime import datetime , timedelta
from users.models import User
from django.db import transaction

class LeadView(APIView):
    def post(self, request):
        try:
            data = request.data
            user = request.user
            print(user.role)
            phone = data["phone"]
            try:
                lead = Lead.objects.get(phone=phone)
                print("LEAD+++++++++>",lead)
                return HttpResponse.Success(data={"lead": LeadResponseSerializer(lead).data, "msg": "lead_already_exist"})
            except ObjectDoesNotExist:
                pass
            # data["assigned_to"] = user.user_id
            # if user.role == ROLES.LOAN_OFFICER.value:
            #     data["assigned_to"] = user.user_id
            # else:
            #     users = User.objects.filter(role=ROLES.LOAN_OFFICER.value)
            #     for i in users:
            #         di[i.username] = Lead.objects.filter(assigned_to=i).count()
            #
            #     sorted_loan_manager_by_leads = sorted(di.items(), key=lambda x: x[1])
            #
            #     data["assigned_to"] = (
            #         User.objects.filter(username=sorted_loan_manager_by_leads[0][0])
            #         .first()
            #         .user_id
            #     )
            data["created_by"] = user.user_id
            data["status"] = LEAD_STATUS.NEW_LEAD.value


            if user.role == ROLES.RELATIONSHIP_MANAGER.value:
                if 'lending_type' not in data or  data["lending_type"] in [LENDING_TYPE.MSME_UNSECURED.value , LENDING_TYPE.MSME_UNSECURED_AGRI.value] :
                    # data["lending_type"] = LENDING_TYPE.MSME_UNSECURED.value
                    data["assigned_to"] = user.user_id
                elif data["lending_type"] == LENDING_TYPE.WELLNESS.value:
                    data["lending_type"] = LENDING_TYPE.WELLNESS.value
                    data["assigned_to"] = user.user_id
                else:
                    data["assigned_to"] = None
            elif user.role == ROLES.LOAN_OFFICER.value:
                if 'lending_type' not in data or data["lending_type"] == LENDING_TYPE.GOLD_LOAN.value:
                    data["lending_type"] = LENDING_TYPE.GOLD_LOAN.value
                    data["assigned_to"] = user.user_id
                elif data["lending_type"] == LENDING_TYPE.WELLNESS.value:
                    data["lending_type"] = LENDING_TYPE.WELLNESS.value
                    data["assigned_to"] = user.user_id
                else:
                    data["assigned_to"] = None
            elif user.role == ROLES.BRANCH_MANAGER.value:
                if 'lending_type' not in data or data["lending_type"] == LENDING_TYPE.GOLD_LOAN.value:
                    data["lending_type"] = LENDING_TYPE.GOLD_LOAN.value
                    data["assigned_to"] = user.user_id
                elif data["lending_type"] == LENDING_TYPE.WELLNESS.value:
                    data["lending_type"] = LENDING_TYPE.WELLNESS.value
                    data["assigned_to"] = user.user_id
                else:
                    data["assigned_to"] = None
            else:
                pass
            
            if data.get("lending_type") in [ LENDING_TYPE.MSME_UNSECURED.value , LENDING_TYPE.MSME_UNSECURED_AGRI.value ]:
                data["lender"] = "b6e03bad-dbe3-494c-b474-b9be297e85aa"
            # data["created_by"] = user.user_id
            # data["status"] = LEAD_STATUS.NEW_LEAD.value
            # account = Account.objects.get(user=user)
            # print(data)
            if data.get("lending_type") in [ LENDING_TYPE.MSME_UNSECURED.value , LENDING_TYPE.MSME_UNSECURED_AGRI.value ]:
                data["lender"] = "b6e03bad-dbe3-494c-b474-b9be297e85aa"
                
            print("DATA+++++++++++++++>",data)
            serializer = LeadCreateSerializer(data=data)

            if serializer.is_valid():
                if data.get("lending_type") == LENDING_TYPE.GOLD_LOAN.value: 
                    lenderId = data.get("lender", None)
                    if lenderId:
                        lenderObj = Lender.objects.filter(lender_id=lenderId)
                        print("lenderObj", lenderObj)
                        print("lenderObj[0].lender_code", lenderObj[0].lender_code)
                        if len(lenderObj) > 0 and lenderObj[0].lender_code == LENDER.AXIS_BANK.value:
                            if not data.get("dob") and not data.get("pan_number") and not data.get("email"):
                                return HttpResponse.BadRequest("PAN , Email and DOB are required.")
                            address_break_down=data.get("address_line")
                            axis_bank_data = {
                                "first_name": data.get("first_name"),
                                "last_name": data.get("last_name"),
                                "city": data.get("city"),
                                "state": data.get("state"),
                                "email": data.get("email"),
                                "address1": address_break_down,
                                "address2": " ",
                                "address3": " ",
                                "dob": data.get("dob"),
                                "pan":data.get("pan_number"),
                                "loan_amount_in_lakhs":data.get("loan_amount_in_lakhs"),
                                "mobile_number": int(data.get("phone").replace("+91",""))
                            }
                                #TODO: for now commenting axis call because we dont have prod credentials
                                # response=AxisBankCalls().create_lead(axis_bank_data)
                                # print("AXIS bank response=======>", response)
                                # if response.get("data",{}).get("Data", None) is None:
                                #     return HttpResponse.Success({"msg":"Failed to create lead at Axis bank"})
                        # else:
                        #     return HttpResponse.BadRequest("PAN and DOB are required.")
                    else:
                        # TODO: will uncomment below check later when axis is back
                        pass
                        # return HttpResponse.BadRequest("Lender ID is required for Gold Loan.")


            serializer.save()

                # FCMService([user]).generateNotification(
                #     title="Radian Finserv", message="Lead Created"
                # )
            return HttpResponse.Success({"lead": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def patch(self, request):
        try:
            data = request.data
            lead = Lead.objects.get(lead_id=request.GET.get("lead_id", ""))
            serializer = LeadCreateSerializer(lead, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"lead": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except Lead.DoesNotExist as e:
            return HttpResponse.BadRequest(e)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def get(self, request):
        try:
            lead = Lead.objects.get(lead_id=request.GET.get("lead_id", ""))
            if not Lead.objects.filter(lead_id=lead.lead_id).exists():
                return HttpResponse.BadRequest("Lead does not exist")
            serializer = LeadDisplaySerializer(lead)
            # print(lead.phone)

            # account=Account.objects.get(user__in=User.objects.filter(phone=lead.phone))

            # print(account)

            return HttpResponse.Success({"lead": serializer.data})
        except Lead.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
    def delete(self, request):
        lead_id=request.data.get('lead_id', None)
        if lead_id is None:
            return resp().response(code=400, data=None, error_msg='Lead id required', error_code=400)
        lead_service=LeadService().delete_obj(lead_id=lead_id)
        return resp().response(code=lead_service.get('status_code'),data=lead_service.get('data'),
                               error_code=lead_service.get('status_code'), error_msg=lead_service.get('data'))
from dashboard.auth import DashboardAPIKeyAuthentication
from rest_framework.permissions import IsAuthenticated

class LeadAllView(APIView, PageNumberPagination):
    authentication_classes = [DashboardAPIKeyAuthentication]
    permission_classes = []

    # def get(self, request):
    #     try:
    #         user = request.user
    #         status = request.GET.get('status', None)
    #         query={}
    #         role=user.role
    #         if status is not None:
    #             query['status'] = status
    #         if user.role == ROLES.LOAN_OFFICER.value:
    #             leads = Lead.objects.filter(assigned_to=user).order_by('-created_at')
    #         elif role in [ROLES.BRANCH_MANAGER.value,
    #                       ROLES.BRANCH_OPERATION_MANAGER.value,
    #                       ROLES.REGIONAL_HEAD.value,
    #                       ROLES.CLUSTER_MANAGER.value]:
    #             # Fetching all branches assigned to current branch manager
    #             bmBranches = BranchUserMapping.objects.filter(user=user)
    #             branches = [b.branch for b in bmBranches]

    #             # fetching all users of the branches fetched above
    #             allUsersOfBranches = BranchUserMapping.objects.filter(
    #                 branch__in=branches
    #             )

    #             allUsers = [u.user for u in allUsersOfBranches]
    #             query['assigned_to__in']=allUsers
    #             query['created_by__in']=allUsers

    #             # Fetching all leads which are assigned or created by users of the branch in which current branch manager works
    #             leads = Lead.objects.filter(
    #                 Q(**query)
    #             ).order_by('-created_at')

    #         elif role in [ROLES.CPC.value, ROLES.AUDIT_ADMIN.value, ROLES.CHIEF_BUSINESS_OPERATOR.value,
    #                       ROLES.BUSINESS_HEAD.value, ROLES.BRANCH_OPERATION_MANAGER.value]:
    #             #filter change start
    #             status = request.GET.get('status', None)
    #             if status is not None:
    #                 query['status__in'] = status.split(",")

    #             loan_manager = request.GET.get('loan_manager', None)
    #             if loan_manager is not None:
    #                 created_by_list = loan_manager.split(",")
    #                 query['created_by__in'] = created_by_list

    #             start_date = request.GET.get('start_date', None)
    #             if start_date:
    #                 query['created_at__gte'] = start_date

    #             end_date = request.GET.get('end_date', None)
    #             if end_date:
    #                 query['created_at__lte'] = end_date

    #             #filter change end
    #             leads = Lead.objects.filter(Q(**query)).order_by('-created_at')
            
    #         else:
    #             leads = []
    #         paginated_data=self.paginate_queryset(leads,request)

    #         serializer = LeadDisplaySerializer(paginated_data, many=True)
    #         # print())
    #         resp_data=self.get_paginated_response(serializer.data).data

    #         resp_data['leads']=resp_data.pop('results')

    #         # return Response(data=resp_data, status=200)
    #         return HttpResponse.Success(resp_data)
    #     except BranchUserMapping.DoesNotExist as e:
    #         traceback.print_exc()
    #         return HttpResponse.InternalServerError(str(e))
    #     except BranchUserMapping.DoesNotExist as e:
    #         traceback.print_exc()
    #         return HttpResponse.InternalServerError(str(e))
    #     except Exception as e:
    #         traceback.print_exc()
    #         return HttpResponse.InternalServerError(str(e))

    def get(self, request):
        try:
            user = request.user
            query = {}
            role = getattr(user, 'role', None)

            apply_filter(request, query)  # Apply filter for all roles

            if role == ROLES.LOAN_OFFICER.value:
                # leads = Lead.objects.filter(assigned_to=user).order_by('-created_at')
                leads = Lead.objects.filter(assigned_to=user).exclude(status=LEAD_STATUS.LEAD_CREATION_COMPLETED.value).order_by('-modified_at')
            elif role == ROLES.RELATIONSHIP_MANAGER.value:
                # leads = Lead.objects.filter(assigned_to=user).order_by('-created_at')
                leads = Lead.objects.filter(assigned_to=user).exclude(status=LEAD_STATUS.LEAD_CREATION_COMPLETED.value).order_by('-modified_at')
            elif role == ROLES.CREDIT_MANAGER.value:
                relationship_manager_ids= User.objects.filter(role=ROLES.RELATIONSHIP_MANAGER.value).values_list('user_id', flat=True)
                leads = Lead.objects.filter(
                    Q(assigned_to__in=relationship_manager_ids) | Q(lending_type=LENDING_TYPE.MSME_UNSECURED.value)
                ).order_by('-modified_at')
            elif role in [ROLES.BRANCH_MANAGER.value,
                        ROLES.BRANCH_OPERATION_MANAGER.value,
                        ROLES.REGIONAL_HEAD.value,
                        ROLES.CLUSTER_MANAGER.value,
                        ROLES.CREDIT_OFFICER.value]:
                bmBranches = BranchUserMapping.objects.filter(user=user)
                branches = [b.branch for b in bmBranches]
                allUsersOfBranches = BranchUserMapping.objects.filter(branch__in=branches)
                allUsers = [u.user for u in allUsersOfBranches]
                query['assigned_to__in'] = allUsers
                query['created_by__in'] = allUsers
                # leads = Lead.objects.filter(Q(**query)).order_by('-created_at')
                leads = Lead.objects.filter(Q(**query)).exclude(status=LEAD_STATUS.LEAD_CREATION_COMPLETED.value).order_by('-modified_at')
            elif role in [ROLES.CPC.value, ROLES.AUDIT_ADMIN.value, ROLES.CHIEF_BUSINESS_OPERATOR.value,
                        ROLES.BUSINESS_HEAD.value, ROLES.BRANCH_OPERATION_MANAGER.value]:
                # leads = Lead.objects.filter(Q(**query)).order_by('-created_at')
                leads = Lead.objects.filter(Q(**query)).order_by('-modified_at')
            else:
                leads = Lead.objects.filter(Q(**query)).order_by('-modified_at')

            paginated_data = self.paginate_queryset(leads, request)
            serializer = LeadDisplaySerializer(paginated_data, many=True)
            resp_data = self.get_paginated_response(serializer.data).data
            resp_data['leads'] = resp_data.pop('results')
            return HttpResponse.Success(resp_data)
        except BranchUserMapping.DoesNotExist as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


def apply_filter(request, query):
    status = request.GET.get('status', None)
    if status is not None:
        query['status__in'] = status.split(",")

    loan_manager = request.GET.get('loan_manager', None)
    if loan_manager is not None:
        created_by_list = loan_manager.split(",")
        query['created_by__in'] = created_by_list


    start_date = request.GET.get('start_date', None)
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        query['created_at__gte'] = start_date_obj.strftime('%Y-%m-%d')

    end_date = request.GET.get('end_date', None)
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')  
        end_date_obj += timedelta(days=1)
        query['created_at__lte'] = end_date_obj.strftime('%Y-%m-%d')


class LeadDocumentView(APIView):
    def post(self, request):
        try:
            user = request.user
            data = request.data

            lead_id = request.GET.get("lead_id", "")
            if not lead_id:
                return HttpResponse.BadRequest("Lead not found")
            
            try:
                lead = Lead.objects.get(lead_id=lead_id)
            except Lead.DoesNotExist:
                return HttpResponse.BadRequest({"error": "Invalid lead ID"})
            with transaction.atomic():
                file = request.FILES.get('file')
                if not file:
                    return HttpResponse.BadRequest({'error': 'No file uploaded'})
                
                doc_type = request.data.get('document_type')
                if not doc_type:
                    return HttpResponse.BadRequest({'error': 'No Document Type added'})
                
                file_name = file.name
                data["file_name"] = file_name
                data["uploaded_by"] = str(user.user_id)
                data["lead"] = lead.lead_id

                # Check if a document with the same type already exists for the lead
                existing_document = lead.lead_document.filter(document_type=doc_type).first()

                if existing_document:
                    # Update the existing document
                    existing_document.file_name = file_name
                    existing_document.file = file
                    existing_document.save()
                    serializer = LeadDocumentSerializer(existing_document)
                else:
                    # Create a new document
                    serializer = LeadDocumentSerializer(data=data)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return HttpResponse.BadRequest(serializer.errors)
                    

                print("LENDER_CODE",lead.lender.lender_code)
                # Define required documents based on lender
                if lead.lender.lender_code == LENDER.FINCARE_SMALL_FINANCE_BANK.value:
                    required_doc_types = [
                        "AADHAR_CARD",
                        "PAN_CARD",
                        "PLEDGE_CARD",
                        "AGRI_PRODUCT_PROOF"
                    ]
                elif lead.lender.lender_code == LENDER.KOTAK_BANK.value:
                    required_doc_types = [
                        "AADHAR_CARD",
                        "PAN_CARD",
                        "PLEDGE_CARD"
                    ]
                else:
                    return HttpResponse.BadRequest({"error": "Unknown lender"})

                # Check if all required document types are present
                existing_doc_types = set(
                    lead.lead_document.filter(
                        document_type__in=required_doc_types
                    ).values_list('document_type', flat=True)
                )
                
                if set(required_doc_types).issubset(existing_doc_types):
                    lead.status = LEAD_STATUS.LEAD_CREATION_COMPLETED.value
                    lead.save()

                return HttpResponse.Success({"lead_doc": serializer.data})

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

        
    def get(self, request):
        try:
            lead =Lead.objects.get(lead_id=request.GET.get("lead_id", ""))
            
            if lead:
                lead_doc = LeadDocument.objects.filter(lead=lead)
                serializer = LeadDocumentSerializer(lead_doc , many=True)
                return HttpResponse.Success({"lead_doc": serializer.data})
            else:
                lead_doc = LeadDocument.objects.all()
                serializer = LeadDocumentSerializer(lead_doc, many=True)
                return HttpResponse.Success({"lead_doc": serializer.data})
        
        except LeadDocument.DoesNotExist:
            return HttpResponse.BadRequest("Lead Document not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def delete(self, request, *args, **kwargs):
        try:
            lead_doc = LeadDocument.objects.get(
                document_id = request.GET.get('document_id',"")
            )
            lead_doc.delete()
            return HttpResponse.Success({"msg": 'Deleted document successfully'})
        except ObjectDoesNotExist:
            return HttpResponse.BadRequest("Document not found")
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
        


# data["assigned_to"] = user.user_id #line32
            # if user.role == ROLES.LOAN_OFFICER.value:
            #     data["assigned_to"] = user.user_id
            # else:
            #     users = User.objects.filter(role=ROLES.LOAN_OFFICER.value)
            #     for i in users:
            #         di[i.username] = Lead.objects.filter(assigned_to=i).count()
            #
            #     sorted_loan_manager_by_leads = sorted(di.items(), key=lambda x: x[1])
            #
            #     data["assigned_to"] = (
            #         User.objects.filter(username=sorted_loan_manager_by_leads[0][0])
            #         .first()
            #         .user_id
            #     )

# data["created_by"] = user.user_id #line 57
            # data["status"] = LEAD_STATUS.NEW_LEAD.value
            # account = Account.objects.get(user=user)
            # print(data)

#TODO: for now commenting axis call because we dont have prod credentials #line86
                                # response=AxisBankCalls().create_lead(axis_bank_data)
                                # print("AXIS bank response=======>", response)
                                # if response.get("data",{}).get("Data", None) is None:
                                #     return HttpResponse.Success({"msg":"Failed to create lead at Axis bank"})



                                # elif lenderObj[0].lender_code in [LENDER.KOTAK_BANK.value , LENDER.FEDRAL_BANK.value]:
                            #     lead_id=serializer.validated_data['lead_id']
                            #     file = request.FILES.get('file')
                            #     if not file:
                            #         return HttpResponse.BadRequest({'error': 'No file uploaded'})
                                
                            #     doc_type=request.data.get('document_type')
                            #     if not doc_type:
                            #         return HttpResponse.BadRequest({'error': 'No Document Type added'})
                                
                            #     file_name=file.name
                            #     data["file_name"] = file_name
                            #     data["uploaded_by"] = str(user.user_id)
                            #     data["lead"] = lead_id
                            #     docserializer = LeadDocumentSerializer(data=data)
                            #     if docserializer.is_valid():
                            #         docserializer.save()
                            #         required_doc_types = [
                            #             "AADHAR_CARD",
                            #             "PAN_CARD", 
                            #             "PLEDGE_CARD", 
                            #             "AGRI_PRODUCT_PROOF"
                            #         ]
                            #         existing_doc_types = set(lead.lead_document.filter(
                            #             document_type__in=required_doc_types
                            #         ).values_list('document_type', flat=True))
                                        
                            #         if set(required_doc_types).issubset(existing_doc_types):
                            #             data["status"] = LEAD_STATUS.LEAD_CREATION_COMPLETED.value