from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework.views import APIView

from document.serializers import DocumentSerializer
from utility.frs.frs_helper import FrsHelper
from utils.envSetup import environment
from ..serializers import BankAccountPostSerializer , AgentBankAccountSerializer
from ..models import BankAccount, AgentBankAccount, AgentAccount
from utils.responseHandler import HttpResponse
from ..models import Account
import traceback
from utils.constants import ACCOUNT_STATUS, KYC_VENDORS, ROLES, BANK_STATEMENT_1, BANK_STATEMENT_2, APPLICANT_TYPE
from ..service.sprint_verify_docs import SprintVerifyDocs


class BankAccountAPI(APIView):
    # TODO: structure below code
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            account_id = request.GET.get("account_id", "")
            account = Account.objects.get(account_id=account_id)
            bank_docs=account.document_account.filter(document_type__in= ["BANK_PASSBOOK","CHEQUE_BOOK", "E_PASSBOOK","BANK_STATEMENT_1","BANK_STATEMENT_2"])
            # if len(bank_docs)==0:
            #     print('error')
            #     return HttpResponse.Success({'msg':'Please upload valid bank documents'})
            if len(bank_docs.filter(document_type__in=["BANK_PASSBOOK", "CHEQUE_BOOK", "E_PASSBOOK"])) == 0:
                return HttpResponse.BadRequest({'msg': 'Please upload at least one valid bank document'})

            # If the role is relationship_manager, check for "BANK_STATEMENT_1" or "BANK_STATEMENT_2"
            if request.user.role == ROLES.RELATIONSHIP_MANAGER.value and len(bank_docs.filter(document_type__in=["BANK_STATEMENT_1", "BANK_STATEMENT_2"])) == 0:
                return HttpResponse.BadRequest({'msg': 'please upload at least Bank Statement'})
            
            account_number = data.get('account_number')
            ifsc_code= data.get('ifsc')
            account_holder=data.get('account_holder_name')

            if BankAccount.objects.filter(account=account, account_number=account_number, ifsc=ifsc_code, verified=True).exists():
                return HttpResponse.Success({'msg':'Bank details already exist'})

            kyc_vendor = environment.KYC_VENDOR
            if kyc_vendor == KYC_VENDORS.RNFI.value:
                response=SprintVerifyDocs().bank_verification({"account_number":account_number,
                                                               "ifsc_code":ifsc_code})
                error=response.get('data').get('msg', None)
                is_verified=True if error is None else False
            else:
                is_verified,error=FrsHelper().process_bank_verification(account_number=account_number,
                                                                        ifsc=ifsc_code,
                                                                        account_holder=account_holder)
            if not is_verified:
                if kyc_vendor==KYC_VENDORS.RNFI.value:
                    return HttpResponse.Success({'msg': error})
                else:
                    if error:

                        msg='frs_limit_reached'
                    else:
                        msg='Please upload valid bank details'
                    return HttpResponse.Success({'msg':msg})

            data['verified']=is_verified
            data["account"] = account_id
            serializer = BankAccountPostSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                if account.status!=ACCOUNT_STATUS.ACCOUNT_CONFIRMED.value:
                    if account.applicant_type==APPLICANT_TYPE.CO_APPLICANT.value:
                        applicant=Account.objects.get(user=account.applicant)
                        applicant.status=ACCOUNT_STATUS.CO_APPLICANT_BANK_DETAILS_ADDED.value
                        applicant.save()
                        account.status=ACCOUNT_STATUS.CO_APPLICANT_BANK_DETAILS_ADDED.value
                    else:
                        account.status = ACCOUNT_STATUS.BANK_DETAILS_ADDED.value
                    account.save()
                data=serializer.data
                data['documents'] = list(bank_docs.values())
                return HttpResponse.Success({"bankaccount": data})
           
            return HttpResponse.BadRequest({"errors" : serializer.errors})
        except BankAccount.DoesNotExist:
            return HttpResponse.Unauthorized("Invalid credentials given")

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def patch(self, request):
        try:
            data = request.data
            account = Account.objects.get(account_id=request.GET.get("account_id", ""))
            bankaccounts = BankAccount.objects.filter(account=str(account), verified=True).first()
            bank_docs=list(account.document_account.filter(document_type__in= ["BANK_PASSBOOK","CHEQUE_BOOK", "E_PASSBOOK"]).values())
            if len(bank_docs)==0:
                return HttpResponse.Success({'msg':'Please upload valid bank documents'})
            if 'account_number' in data.keys() and data['account_number']!=bankaccounts.account_number:
                is_verified,error = FrsHelper().process_bank_verification(account_number=data['account_number'],
                                                                    ifsc=data['ifsc'],account_holder=data.get('account_holder_name'))
                if not is_verified:
                    error = error.get('message', None)
                    if error:
                        msg = 'frs_limit_reached'
                    else:
                        msg = 'Please upload valid bank details'
                    return HttpResponse.Success({'msg': msg})
                data['verified'] = is_verified
            serializer = BankAccountPostSerializer(bankaccounts, data=data, partial=True)
            if serializer.is_valid():
                 serializer.save()
                 data=serializer.data
                 #data['documents']=bank_docs
                 return HttpResponse.Success({"bankaccount": data})
            return HttpResponse.BadRequest(serializer.errors)
        except BankAccount.DoesNotExist as e:
             return HttpResponse.BadRequest(e)
        except Exception as e:
             traceback.print_exc()
             return HttpResponse.InternalServerError(str(e))

    def get(self, request):
        try:
            account = Account.objects.get(account_id=request.GET.get("account_id", ""))
            # bankaccounts = BankAccount.objects.filter(account=account, account_purpose=request.GET.get("account_purpose", ""))
            account_purpose = request.GET.get("account_purpose", "")

            if account_purpose:
                bankaccounts = BankAccount.objects.filter(account=account, account_purpose=account_purpose)
            else:
                bankaccounts = BankAccount.objects.filter(account=account, account_purpose="LOAN_DISBURSEMENT")
            bank_docs=account.document_account.filter(document_type__in= ["BANK_PASSBOOK","CHEQUE_BOOK","E_PASSBOOK", "BANK_STATEMENT_1", "BANK_STATEMENT_2"])
            serializer = BankAccountPostSerializer(bankaccounts, many=True)
            data=serializer.data
            resp=[]
            for i in data:
                i['documents']=DocumentSerializer(bank_docs, many=True).data
                resp.append(i)
            return HttpResponse.Success({"bankaccounts": resp})
        except BankAccount.DoesNotExist as e:
            return HttpResponse.BadRequest(str(e))
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        


class AgentBankAccountView(APIView):

    def get_agent_account(self, user):
        return self.get_latest_agent_account(user=user)

    def get_latest_agent_account(self, user=None, user_id=None, agent_account_id=None):
        try:
            queryset = AgentAccount.objects.all()

            if agent_account_id:
                queryset = queryset.filter(id=agent_account_id)
            elif user_id:
                queryset = queryset.filter(user__user_id=user_id)
            elif user is not None:
                queryset = queryset.filter(user=user)
            else:
                return None

            return queryset.order_by("-created_at", "-modified_at").first()
        except (TypeError, ValueError, ValidationError):
            return None

    def post(self, request):
        try:
            data = request.data.copy()

            user_id = request.GET.get("user_id")
            agent_account_id = request.GET.get("agent_account_id")
            agent = self.get_latest_agent_account(
                user_id=user_id,
                agent_account_id=agent_account_id,
                user=request.user if not user_id and not agent_account_id else None,
            )

            if not agent:
                return HttpResponse.BadRequest("AgentAccount not found")

            data["agent"] = str(agent.id)
            serializer = AgentBankAccountSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    # Keep a single active bank account for the selected agent profile.
                    AgentBankAccount.objects.filter(agent=agent).delete()
                    serializer.save()
                return HttpResponse.Success({"bank_account": serializer.data})

            return HttpResponse.BadRequest(serializer.errors)

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def get(self, request):
        try:
            user_id = request.GET.get("user_id")
            agent_account_id = request.GET.get("agent_account_id")

            if user_id or agent_account_id:
                # Return specific agent's bank account
                agent_account = self.get_latest_agent_account(
                    user_id=user_id,
                    agent_account_id=agent_account_id,
                )
                if not agent_account:
                    return HttpResponse.BadRequest("AgentAccount not found")

                bank = AgentBankAccount.objects.filter(agent=agent_account).first()
                if not bank:
                    return HttpResponse.BadRequest("Bank account not found")

                serializer = AgentBankAccountSerializer(bank)
                return HttpResponse.Success({"bank_account": serializer.data})

            else:
                # Return all bank accounts
                banks = AgentBankAccount.objects.all()
                serializer = AgentBankAccountSerializer(banks, many=True)
                return HttpResponse.Success({"bank_accounts": serializer.data})

        except AgentAccount.DoesNotExist:
            return HttpResponse.BadRequest("AgentAccount not found")

        except AgentBankAccount.DoesNotExist:
            return HttpResponse.BadRequest("Bank account not found")

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))



    def patch(self, request):
        try:
            data = request.data
            bank_account_id = request.GET.get("bank_account_id", "")

            # Correct field name
            bank = AgentBankAccount.objects.get(Agent_bank_account_id=bank_account_id)

            if data.get("verified") is True:
                data["verified"] = True

            serializer = AgentBankAccountSerializer(bank, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"bank_account": serializer.data})

            return HttpResponse.BadRequest(serializer.errors)

        except AgentBankAccount.DoesNotExist:
            return HttpResponse.BadRequest("Bank account not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))



    def delete(self, request):
        try:
            bank_account_id = request.GET.get("bank_account_id", "")

            # Correct field name
            bank = AgentBankAccount.objects.get(Agent_bank_account_id=bank_account_id)
            bank.delete()

            return HttpResponse.Success({"msg": "Bank account deleted successfully"})

        except AgentBankAccount.DoesNotExist:
            return HttpResponse.BadRequest("Bank account not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
