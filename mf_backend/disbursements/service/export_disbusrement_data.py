from disbursements.models import Disbursement
from account.models import BankAccount
from datetime import datetime
from utils.responseHandler import HttpResponse
from application.serializers import ApplicationOverviewSerializer


class ExportDisbursementService():

    def exportDisbursement(self, request):
          
            disbursement_ids = request.GET.get('disbursement_ids', "").split(",")
            if not disbursement_ids:
                return None
            else:
                disbursements = Disbursement.objects.filter(disbursement_id__in=disbursement_ids)
                disbursementData = []

                for d in disbursements:
                        
                        singledisbursementData = []
                        singledisbursementData.append(str("22200000003101"))
                        user = d.application.account
                        try:
                            bank_account = BankAccount.objects.get(account=user)
                            account_no = (bank_account.account_number)
                        except BankAccount.DoesNotExist:
                            account_no = ""
                        singledisbursementData.append(str(account_no))
                        singledisbursementData.append(d.application.account.user.first_name+" "+d.application.account.user.last_name)
                        if d.disbursement_amount:
                            singledisbursementData.append(int(d.disbursement_amount))
                        else:
                            singledisbursementData.append(0)
                        payment_mode = "R" if d.disbursement_amount >= 200000 else "N"
                        singledisbursementData.append(payment_mode)
                        try:
                            bank_account = BankAccount.objects.get(account=user)
                            ifsc = bank_account.ifsc
                        except BankAccount.DoesNotExist:
                                ifsc = ""
                        singledisbursementData.append(ifsc)
                        singledisbursementData.append(d.application.lender)
                        singledisbursementData.append(d.application.application_type)
                        try:
                            branch_info = ApplicationOverviewSerializer().get_branch(d.application)
                            branch_code = branch_info.get('branch_code', '')
                            employee_id = str(d.application.Originatedby.employee_id or "")
                            disbursement_id = str(d.disbursement_id or "")
                        except (Disbursement.DoesNotExist):
                            continue
                        unique_id = "_".join(filter(None, [branch_code, employee_id, disbursement_id]))
                        singledisbursementData.append(unique_id)
                        disbursementData.append(singledisbursementData)
                disbursements.update(payment_status=1)
                return disbursementData
                    

