from rest_framework.pagination import PageNumberPagination
from users.models import User
from rest_framework.views import APIView
from ..models import Account, AgentAccount
from ..serializers import CustomerDisplayAccountSerializer, CreateAccountRequestSerializer, AccountModelSerializer, \
    NomineeDetailsSerializer, AgentAccountSerializer
from rest_framework.response import Response
from document.utils.document_utils import DocumentUtils
from users.serializers import AddressesSerializer
from users.service.userService import UserService
from utils.responseHandler import HttpResponse
from ..service.accountService import AccountService
import traceback
from utils.constants import LEAD_STATUS, ACCOUNT_STATUS, ROLES ,APPLICANT_TYPE
from lead.models import Lead
from lead.serializers import LeadResponseSerializer
from branch.models import BranchUserMapping
from utils import constants
from rest_framework import status
import logging
from utility.response_handler import HttpResponse as resp
from django.db.models import Q
from dateutil import parser as parser
from datetime import datetime , timezone , timedelta
from django.utils import timezone as tz
from reference_pd.models import Reference_PD
from reference_pd.serializer import Reference_PDSerializer
from credit_status.models import CreditStatus
from credit_status.serializers import CreditStatusGETSerializer
from loan.models import GprsPhotos
from loan.serializer import GPRSDocSerializer
from django.db import transaction


log = logging.getLogger('logs')


AGENT_USER_SYNC_FIELDS = ("email", "city", "state", "pincode")


def _validate_agent_pincode(data):
    if "pincode" not in data:
        return None

    pincode = data.get("pincode")
    if pincode in (None, ""):
        return None

    pincode = str(pincode).strip()
    if not pincode.isdigit() or len(pincode) != 6:
        return {"pincode": ["Pincode must be 6 digits"]}

    data["pincode"] = pincode
    return None


def _sync_user_from_agent_payload(user, payload):
    update_fields = []

    full_name = payload.get("full_name")
    if full_name is not None:
        full_name = str(full_name).strip()
        if full_name:
            name_parts = full_name.split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
        else:
            first_name = ""
            last_name = ""
        if user.first_name != first_name:
            user.first_name = first_name
            update_fields.append("first_name")
        if user.last_name != last_name:
            user.last_name = last_name
            update_fields.append("last_name")

    for field in AGENT_USER_SYNC_FIELDS:
        if field in payload:
            value = payload.get(field)
            if value == "":
                value = None
            if getattr(user, field) != value:
                setattr(user, field, value)
                update_fields.append(field)

    if update_fields:
        user.save(update_fields=update_fields)


class AgentOnboardingStatusAPIView(APIView):
    def get(self, request):
        try:
            user_id = request.GET.get("user_id", None)
            if user_id:
                exists = AgentAccount.objects.filter(user__user_id=user_id).exists()
            else:
                exists = AgentAccount.objects.filter(user=request.user).exists()
            return HttpResponse.Success({"is_onboarding_complete": bool(exists)})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class CustomerAccount(APIView, PageNumberPagination):

    # def get(self,request, *args, **kwargs):
    #     try:
    #         #filter change start 
    #         query={}
    #         #filter change end

    #         # user=User.objects.get(username=request.user)
    #         # print(user.role)
    #         role = request.user.role
            
    #         account_id = request.GET.get("account_id",None)
    #         if account_id is not None:
    #             customers=Account.objects.get(account_id=account_id)
    #             resp = CustomerDisplayAccountSerializer(customers).data
    #             nominee_details = customers.nomieedetails_account.all()
    #             resp['nominee'] = NomineeDetailsSerializer(nominee_details, many=True).data
    #             return HttpResponse.Success({'customers':resp})

    #         else:
    #             if role == ROLES.CPC.value \
    #                     or role==ROLES.CHIEF_BUSINESS_OPERATOR.value \
    #                     or role==ROLES.BUSINESS_HEAD.value\
    #                     or role==ROLES.AUDIT_ADMIN.value:
                    
    #                 #filter change start 
    #                 branch=request.GET.get('branch', None)
    #                 if branch is not None:
    #                     branches = BranchUserMapping.objects.filter(branch__branch_id=branch)
    #                     allBranchUsers = [b.user for b in branches]
    #                     query['created_by__in']=allBranchUsers

    #                 start_date = request.GET.get('start_date', None)
    #                 if start_date:
    #                     query['created_at__gte'] = start_date

    #                 end_date = request.GET.get('end_date', None)
    #                 if end_date:
    #                     query['created_at__lte'] = end_date

    #                 created_by = request.GET.get('created_by', None)
    #                 if created_by is not None:
    #                     created_by_list = created_by.split(",")
    #                     query['created_by__in'] = created_by_list

    #                 #filter change end
                        
    #                 customers=Account.objects.filter(Q(**query)).order_by('-modefied_at')
                    
    #             elif role in [ROLES.BRANCH_MANAGER.value, ROLES.CLUSTER_MANAGER.value, ROLES.REGIONAL_HEAD.value, ROLES.BRANCH_OPERATION_MANAGER.value]:
    #                 branchUserMap = BranchUserMapping.objects.get(user=request.user)
    #                 customers=Account.objects.filter(branch=branchUserMap.branch).order_by('-modefied_at')
    #             elif role == ROLES.LOAN_OFFICER.value:
    #                 customers=Account.objects.filter(created_by=request.user).order_by('-modefied_at')
    #             else:
    #                 return HttpResponse.Forbidden(errorMsg="Not Allowed")
    #             paginated_data=self.paginate_queryset(customers, request)
    #             resp = CustomerDisplayAccountSerializer(paginated_data,many=True).data
    #             resp=self.get_paginated_response(resp).data
    #             resp['customers']=resp.pop('results')
    #         return HttpResponse.Success(resp)
            
                
            
    #         # resp=Response( { "status":"success","data":serializer.data})
    #         # return resp
    #     except Account.DoesNotExist as e:
    #         return HttpResponse.Unauthorized('Invalid credentials given')


    def get(self, request, *args, **kwargs):
        try:
            role = request.user.role
            account_id = request.GET.get("account_id", None)

            if account_id is not None:
                customers = Account.objects.get(account_id=account_id)
                resp = CustomerDisplayAccountSerializer(customers).data
                co_applicant = Account.objects.filter(
                    applicant=customers.user, 
                    applicant_type=APPLICANT_TYPE.CO_APPLICANT.value
                ).all() 
                resp['co_applicant'] = CustomerDisplayAccountSerializer(co_applicant, many=True).data
                nominee_details = customers.nomieedetails_account.all()
                resp['nominee'] = NomineeDetailsSerializer(nominee_details, many=True).data
                lead_details = Lead.objects.filter(account=account_id)  # Adjust based on the actual relationship field
                resp['lead'] = LeadResponseSerializer(lead_details , many=True).data
                credit_status = CreditStatus.objects.filter(account=account_id)  # Adjust based on the actual relationship field
                resp['credit_status'] = CreditStatusGETSerializer(credit_status , many=True).data
                reference_pd = Reference_PD.objects.filter(account=account_id)  # Adjust based on the actual relationship field
                resp['reference_pd'] = Reference_PDSerializer(reference_pd , many=True).data
                gprs_photos = GprsPhotos.objects.filter(account=account_id)  # Adjust based on the actual relationship field
                resp['gprs_photos'] = GPRSDocSerializer(gprs_photos , many=True).data
                return HttpResponse.Success({'customers': resp})
                
            else:
                query = apply_filters(request)

                if role in [ROLES.CPC.value, ROLES.CHIEF_BUSINESS_OPERATOR.value, ROLES.BUSINESS_HEAD.value, ROLES.AUDIT_ADMIN.value]:
                    customers = Account.objects.filter(Q(**query)).order_by('-modefied_at')
                elif role == ROLES.CREDIT_MANAGER.value:
                    customers = Account.objects.filter(created_by__role=ROLES.RELATIONSHIP_MANAGER.value, **query).order_by('-modefied_at')
                elif role in [ROLES.BRANCH_MANAGER.value, ROLES.CLUSTER_MANAGER.value, ROLES.REGIONAL_HEAD.value, ROLES.BRANCH_OPERATION_MANAGER.value]:
                    # branchUserMap = BranchUserMapping.objects.get(user=request.user)
                    # customers = Account.objects.filter(branch=branchUserMap.branch, **query).order_by('-modefied_at')
                    branchUserMap = BranchUserMapping.objects.get(user=request.user)
                    customers = Account.objects.filter(
                        branch=branchUserMap.branch,
                        created_by__role=ROLES.LOAN_OFFICER.value,
                        **query
                    ).order_by('-modefied_at')
                elif role == ROLES.LOAN_OFFICER.value:
                    customers = Account.objects.filter(created_by=request.user, **query).order_by('-modefied_at')
                elif role == ROLES.RELATIONSHIP_MANAGER.value:
                    customers = Account.objects.filter(created_by=request.user, **query).order_by('-modefied_at')
                # elif role == ROLES.CREDIT_OFFICER.value:
                #     branchUserMap = BranchUserMapping.objects.get(user=request.user)
                #     customers = Account.objects.filter(branch=branchUserMap.branch, **query).order_by('-modefied_at')
                elif role == ROLES.CREDIT_OFFICER.value:
                    branchUserMap = BranchUserMapping.objects.get(user=request.user)
                    customers = Account.objects.filter(
                        branch=branchUserMap.branch,
                        created_by__role=ROLES.RELATIONSHIP_MANAGER.value,
                        **query
                    ).order_by('-modefied_at')
                else:
                    return HttpResponse.Forbidden(errorMsg="Not Allowed")

                paginated_data = self.paginate_queryset(customers, request)
                resp = CustomerDisplayAccountSerializer(paginated_data, many=True).data

                for customer in resp:
                    
                    account_id = customer['account_id']
                    account=Account.objects.get(account_id=account_id)
                    customer['lead'] = LeadResponseSerializer(
                        Lead.objects.filter(account=account_id), many=True
                    ).data
                    customer['credit_status'] = CreditStatusGETSerializer(
                        CreditStatus.objects.filter(account=account_id), many=True
                    ).data
                    customer['co_applicant'] = CustomerDisplayAccountSerializer(Account.objects.filter(
                    applicant=account.user, 
                    applicant_type=APPLICANT_TYPE.CO_APPLICANT.value), many=True
                    ).data
                    customer['reference_pd'] = Reference_PDSerializer(
                        Reference_PD.objects.filter(account=account_id), many=True
                    ).data
                    customer['gprs_photos'] = GPRSDocSerializer(
                        GprsPhotos.objects.filter(account=account_id), many=True
                    ).data
                resp = self.get_paginated_response(resp).data
                resp['customers'] = resp.pop('results')
                return HttpResponse.Success(resp)

        except Account.DoesNotExist:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            return HttpResponse.BadRequest(str(e))
        
    def delete(self, request):
        account_id = request.data.get('account_id', None)
        if account_id is None:
            return resp().response(code=400, data=None, error_msg='account_id required', error_code=400)
        account_service = AccountService().delete_account(account_id=account_id)
        return resp().response(code= account_service.get('status_code'), data=account_service.get('data'),
                               error_code=account_service.get('status_code'), error_msg=account_service.get('data'))

    def post(self,request, *args, **kwargs):

        try :
            data=request.data.copy()
            service = AccountService()

            user_data=service.check_if_account_exist(data)

            if user_data:
                if user_data.role==ROLES.CUSTOMER:
                    return HttpResponse.Success({'account': AccountModelSerializer(user_data).data,
                                             "msg":"account_already_exists"}
                                            )
                return HttpResponse.BadRequest(errorMsg=f'User with role {user_data.role} already exist with phone {user_data.phone}')


                # return HttpResponse.Success(AccountModelSerializer(Account.objects.get(user=user)).data)


            accSer=CreateAccountRequestSerializer(data=data)

            if accSer.is_valid():
                lead = None  # Default value
                lead_id = accSer.validated_data.get('lead_id')  # Use .get() to avoid KeyError

                if lead_id:  # Check if lead_id exists and is not empty
                    try:
                        lead = Lead.objects.get(lead_id=lead_id)
                    except Lead.DoesNotExist:
                        lead = None

                
                # TODO: should send username and password to user via mail or sms.
                user=UserService().createUsers({
                    'first_name': accSer.validated_data['first_name'],
                    'last_name': accSer.validated_data['last_name'],
                    'phone': accSer.validated_data['phone'],
                })
                if not user:
                    return HttpResponse.InternalServerError('User creation failed')
                
                doc = DocumentUtils(request.user).upload_document(file=request.data.get('profile_photo'),document_type="CUSTOMER_PROFILE_PIC")
                
                cif_number=service.generate_cif_number()
                print(cif_number)
                
                accountData = accSer.validated_data.copy()
                accountData["customer_id"]=str(cif_number)
                accountData['user'] = user
                accountData['created_by'] = request.user
                accountData['profile_photo'] = doc
                # accountData['status']= ACCOUNT_STATUS.NEW_ACCOUNT_CREATED.value
                accountData['status'] = (
                    ACCOUNT_STATUS.CO_APPLICANT_NEW_ACCOUNT_CREATED.value
                    if accSer.validated_data.get('applicant_type') == APPLICANT_TYPE.CO_APPLICANT.value
                    else ACCOUNT_STATUS.NEW_ACCOUNT_CREATED.value
                )

                

                accountData.pop('lead_id', None)
                del accountData['first_name']
                del accountData['last_name']
                del accountData['phone']
                with transaction.atomic():
                    account = Account.objects.create(**accountData)
                    print("1")

                    if accSer.validated_data.get('applicant_type') == APPLICANT_TYPE.CO_APPLICANT.value:
                        applicant=Account.objects.get(user=accSer.validated_data.get('applicant'))
                        applicant.status=ACCOUNT_STATUS.CO_APPLICANT_NEW_ACCOUNT_CREATED.value
                        applicant.save()
                    print("2")
                    # Serialize the lead
                    lead_data = None
                    if lead is not None :
                        lead_data = LeadResponseSerializer(lead).data
                        lead.status=LEAD_STATUS.LEAD_ACCOUNT_CREATED.value
                        lead.account = account
                        lead.save()
                    # account.status=ACCOUNT_STATUS.NEW_ACCOUNT_CREATED.value
                    # account.save()
                    account_serialized = AccountModelSerializer(account).data
                    account_serialized['lead'] = lead_data
                    
                    #resp=HttpResponse.Success({'account':AccountModelSerializer(account).data})
                    resp=HttpResponse.Success({'account':account_serialized})
                    return resp

            else:
                # errors = accSer.errors
                # errors.update(userSer.errors)
                return HttpResponse.BadRequest(accSer.errors)
                
        except Lead.DoesNotExist as e:
            return HttpResponse.BadRequest('Invalid lead_id')
        except Account.DoesNotExist as e:
            return HttpResponse.Unauthorized('Invalid credentials given')
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
            
    def patch(self, request, *args, **kwargs):
        data = request.data
        account_id = data.get("account_id")
        if not account_id:
            return Response({
                "error": constants.ACCOUNT_ID_NOT_NULL
            }, status=status.HTTP_200_OK)
        log.info("Update Account Request received: " + str(data))
        try:
            account = Account.objects.get(account_id=account_id)
            profile_photo = data.get("profile_photo", None)
            if profile_photo:
                profile_id = account.profile_photo.document_id
                doc = DocumentUtils(request.user).update_document(file=profile_photo,document_type="CUSTOMER_PROFILE_PIC", document_id=profile_id, file_name=profile_photo.name)
            account = Account.objects.get(account_id=account_id)
            acc_ser = AccountModelSerializer(account, data=data, partial=True)
            if acc_ser.is_valid():
                acc_ser.save()
                resp = Response({
                    "status": "success",
                    "data":acc_ser.data
                }, status=status.HTTP_200_OK)
                log.info("Response : %s", str(resp.data))
            else:
                resp = Response({
                    "errors": acc_ser.errors
                }, status=status.HTTP_200_OK)
                log.info("Response : %s", str(resp.data))
            return resp
        except Exception as ve:
            log.exception("Exception Occured!")
            return Response({
                "error": str(ve)
            }, status=status.HTTP_200_OK)
            
    '''@action(methods=['get'],detail=True,url_path='getAccount/')    
    def getAccount(self, request, *args, **kwargs):
        user = request.user
        account_id = request.GET.get("account_id")
        try:
            account = Account.objects.get(account_id=account_id)
            serializer=CustomerDisplayAccountSerializer(account)
            return HttpResponse.Success({'account': serializer.data})
        except Exception as ve:
            log.exception("Exception Occured!")
            return Response({
                "error": str(ve)
            }, status=status.HTTP_200_OK)'''
        
def apply_filters(request):
    query = {}

    branch = request.GET.get('branch', None)
    if branch is not None:
        branches = branch.split(",") 
        allBranchUsers = []
        for branch_id in branches:
            branch_users = BranchUserMapping.objects.filter(branch__branch_id=branch_id)
            allBranchUsers.extend([b.user for b in branch_users])
        query['created_by__in'] = allBranchUsers

    start_date = request.GET.get('start_date', None)
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        query['created_at__gte'] = start_date_obj.strftime('%Y-%m-%d')

    end_date = request.GET.get('end_date', None)
    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')  
        end_date_obj += timedelta(days=1)
        query['created_at__lte'] = end_date_obj.strftime('%Y-%m-%d')

    created_by = request.GET.get('created_by', None)
    if created_by is not None:
        created_by_list = created_by.split(",")
        query['created_by__in'] = created_by_list

    applicant_type = request.GET.get('applicant_type', None)
    if applicant_type is not None:
        query['applicant_type'] = applicant_type

    return query




class AgentAccountAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self,request):
        try:
            data = request.data.copy()
            user = request.user
            # If anonymous (no auth), pick the first user as a system-level fallback
            if not user or user.is_anonymous:
                user = User.objects.order_by('date_joined').first()
            if user:
                data["user"] = str(user.user_id)
                data["created_by"] = str(user.user_id)
                data["modified_by"] = str(user.user_id)

            pincode_error = _validate_agent_pincode(data)
            if pincode_error:
                return HttpResponse.BadRequest(pincode_error)

            with transaction.atomic():
                _sync_user_from_agent_payload(user=user, payload=data)

                serializer = AgentAccountSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()

                    return HttpResponse.Success({"account": serializer.data})

                return HttpResponse.BadRequest(serializer.errors)

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def get(self, request):
        try:
            user = request.user
            params = request.query_params
            query = {}

            # Pagination
            page_limit = 10
            pg = request.GET.get("pg", "1")
            try:
                page_no = int(pg)
                offset = (page_no - 1) * page_limit
            except ValueError:
                return HttpResponse.BadRequest("Invalid 'pg' param, must be integer.")

            # Filters
            account_id = request.GET.get("id")
            user_id = request.GET.get("user")

            if account_id:
                query["id"] = account_id
            if user_id:
                query["user__user_id"] = user_id

            # Query execution
            accounts = AgentAccount.objects.filter(Q(**query)).order_by("-created_at")[offset: offset + page_limit]
            serializer = AgentAccountSerializer(accounts, many=True, context={"request": request})
            return HttpResponse.Success({"account": serializer.data})

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def patch(self, request):
        try:
            account_id = request.GET.get("account_id", "")
            if not account_id:
                return HttpResponse.BadRequest("account_id is required!")

            try:
                account = AgentAccount.objects.get(id=account_id)
            except AgentAccount.DoesNotExist:
                return HttpResponse.BadRequest("AgentAccount not found")

            data = request.data.copy()
            pincode_error = _validate_agent_pincode(data)
            if pincode_error:
                return HttpResponse.BadRequest(pincode_error)

            serializer = AgentAccountSerializer(account, data=data, partial=True, context={"request": request})
            if serializer.is_valid():
                with transaction.atomic():
                    modifier = request.user if request.user and not request.user.is_anonymous else User.objects.first()
                    updated_account = serializer.save(modified_by=modifier)
                    _sync_user_from_agent_payload(user=updated_account.user, payload=data)
                return HttpResponse.Success({"agent_account": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def delete(self, request):
        try:
            account_id = request.GET.get("account_id", "")
            if not account_id:
                return HttpResponse.BadRequest("account_id is required!")

            try:
                account = AgentAccount.objects.get(id=account_id)
            except AgentAccount.DoesNotExist:
                return HttpResponse.BadRequest("AgentAccount not found")

            account.delete()
            return HttpResponse.Success({"msg": "AgentAccount deleted successfully"})

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))





