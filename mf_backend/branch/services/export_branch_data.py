from branch.models import Branch
from application.models import Application
from loan.models import Loan
from datetime import datetime
from utils.responseHandler import HttpResponse
from django.db.models import Sum
from utils.constants import APPLICATION_STATUS



class ExportBranchService():

    def exportBranch(self, request):
          
            
                branches = Branch.objects.all()
                branchData = []

                for b in branches:
                        
                        singleBranchData = []
                        singleBranchData.append(b.branch_code)
                        singleBranchData.append(b.branch_name)
                        singleBranchData.append(b.branch_manager)

                        total_applications = Application.objects.filter(branch=b).count()
                        singleBranchData.append(total_applications)

                        total_loans = Loan.objects.filter(branch=b).count()
                        singleBranchData.append(total_loans)

                        total_disbursal = Application.objects.filter(branch=b).aggregate(Sum('disbursal_amount'))['disbursal_amount__sum']
                        singleBranchData.append(total_disbursal or 0)

                        total_disbursed = Application.objects.filter(branch=b).aggregate(Sum('disbursed_amount'))['disbursed_amount__sum']
                        singleBranchData.append(total_disbursed or 0)

                        total_net_disbursed = Application.objects.filter(branch=b).aggregate(Sum('net_disbursed_amount'))['net_disbursed_amount__sum']
                        singleBranchData.append(total_net_disbursed or 0)

                        total_weight = Application.objects.filter(branch=b).aggregate(Sum('total_weight'))['total_weight__sum']
                        singleBranchData.append(int(total_weight or 0))

                        total_net_weight = Application.objects.filter(branch=b).aggregate(Sum('net_weight'))['net_weight__sum']
                        singleBranchData.append(int(total_net_weight or 0))

                        total_loan_amount = Loan.objects.filter(branch=b).aggregate(Sum('loan_amount'))['loan_amount__sum']
                        singleBranchData.append(total_loan_amount or 0)

                        total_goods_price = Loan.objects.filter(branch=b).aggregate(Sum('total_goods_price'))['total_goods_price__sum']
                        singleBranchData.append(int(total_goods_price or 0))

                        takeover_applications = Application.objects.filter(branch=b, status=APPLICATION_STATUS.TAKE_OVER.value).count()
                        singleBranchData.append(takeover_applications)

                        takeover_applications = Application.objects.filter(branch=b, status=APPLICATION_STATUS.APPLICATION_REJECTED_BY_CPC.value).count()
                        singleBranchData.append(takeover_applications)

                        











                        branchData.append(singleBranchData)
                
                return branchData
                    

