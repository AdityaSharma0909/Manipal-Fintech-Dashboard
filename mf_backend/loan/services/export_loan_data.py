from loan.models import Loan
from account.models import BankAccount
from django.db.models import Q

import operator
from functools import reduce

class ExportLoanServices():

#     def exportLoan(self, request):
        
#           loansData = []
#           queries = {}

#           startDate = request.GET.get('start_date', None)
#           if startDate:
#                queries.append(Q(created_at__gte=startDate))
               
#           endDate = request.GET.get('end_date', None)
#           if endDate:
#                queries.append(Q(created_at__lte=endDate))

#           status = request.GET.get('status' , None)
#           if status :
#                queries.append(Q(status__in=status.split(','))) 

#           amortization_type = request.GET.get('amortization_type' , None)
#           if amortization_type:
#                queries.append(Q(amortization_type__in=amortization_type.split(',')))

#           product_name = request.GET.get('product_name', None)
#           if product_name:
#                queries.append(Q(product__product_name__in=product_name.split(',')))

#           product_id = request.GET.get('product_id', None)
#           if product_id:
#                queries.append(Q(product__product_id__in=product_id.split(',')))

#           tenure_min = request.GET.get('tenure' , None)
#           if tenure_min:
#                queries.append(Q(tenure__gte=tenure_min))

#           tenure_max = request.GET.get('tenure' , None)
#           if tenure_max:
#                queries.append(Q(tenure__lte=tenure_max))

#           lender_name = request.GET.get('lender_name', None)
#           if lender_name:
#                queries.append(Q(lender__lender_name__in=lender_name.split(',')))
          
#           loan_amount_range_min = request.GET.get('loan_amount_range' , None)
#           if loan_amount_range_min:
#                queries.append(Q(loan_amount_range__gte=loan_amount_range_min)) 

#           loan_amount_range_max = request.GET.get('loan_amount_range' , None)
#           if loan_amount_range_max:
#                queries.append(Q(loan_amount_range__lte=loan_amount_range_max))

#           loan_type = request.GET.get('loan_type' , None)
#           if loan_type:
#                queries.append(Q(loan_type__in=loan_type.split(',')))

#           purpose_of_loan = request.GET.get('purpose of loan', None)
#           if purpose_of_loan:
#                queries.append(Q(purpose_of_loan__in=status.split(',')))

#           total_weight = request.GET.get('total_weight' , None)
#           if total_weight:
#                queries.append(Q(total_weight=total_weight))

#           total_weight_min = request.GET.get('total_weight__min' , None)
#           if total_weight_min:
#                queries.append(Q(total_weight__gte=total_weight_min))

#           total_weight_max = request.GET.get(' total_weight__max' , None)
#           if  total_weight_max:
#                queries.append(Q( total_weight__lte=total_weight_max))

#           net_weight = request.GET.get('net_weight' , None)
#           if net_weight:
#                queries.append(Q(net_weight__gte=net_weight))

#           net_weight_min = request.GET.get('net_weight__min' , None)
#           if net_weight_min:
#                queries.append(Q(net_weight__gte=net_weight_min))

#           net_weight_max = request.GET.get('net_weight__max' , None)
#           if net_weight_max:
#                queries.append(Q(net_weight__lte=net_weight_max))

#           originated_by = request.GET.get('originated_by ', None)
#           if originated_by :
#                queries.append(Q(originated_by = originated_by.split(',')))

#           disbursed_date_start = request.GET.get('disbursed_date' , None)
#           if disbursed_date_start:
#                queries.append(Q(disbursed_date__gte=disbursed_date_start))

#           disbursed_date_end = request.GET.get('disbursed_date' , None)
#           if disbursed_date_end:
#                queries.append(Q(disbursed_date__lte=disbursed_date_end))



#           filter_query = {}
          
#           if len(queries)>0:
#                q = reduce(operator.and_,queries)
#                loans = Loan.objects.filter(q)
#           else:
#                loans = Loan.objects.all()    

#           bank = Loan.objects.filter(**queries).prefetch_related(
#                'application__account__bankaccount_account',
          
#           )
          
              

          
#           singleLoanData = []
#           for l in loans:
#                bank_details =l.application.account.bankaccount_account.all().first()

#                singleLoanData.append(l.loan_number)
#                singleLoanData.append(l.status)
#                singleLoanData.append(l.application.account.user.first_name + " "+ l.application.account.user.last_name)
#                singleLoanData.append(l.application.account.email)
#                singleLoanData.append(l.application.account.gender)
#                singleLoanData.append(l.application.account.year_of_birth.strftime("%d/%m/%Y ,%H:%M"))
#                singleLoanData.append(l.application.account.user.phone)
#                singleLoanData.append(l.application.account.occupation)
#                singleLoanData.append(l.application.account.net_annual_income)
#                singleLoanData.append(l.application.account.aadhar_no)
#                singleLoanData.append(l.application.account.pan_no)
#                singleLoanData.append(l.application.account.mother_name)
#                singleLoanData.append(l.application.account.father_name)
#                singleLoanData.append(l.application.account.spouse_name)
#                singleLoanData.append(l.application.account.education)
#                singleLoanData.append(l.application.account.religion)
#                singleLoanData.append(l.application.account.nationality)
#                singleLoanData.append(l.application.account.disablity)
#                singleLoanData.append(bank_details.bank_name if bank_details else "",)
#                singleLoanData.append(bank_details.account_number if bank_details else "",)
#                singleLoanData.append(bank_details.ifsc if bank_details else "",)
#                singleLoanData.append(bank_details.account_holder_name if bank_details else "",)
#                singleLoanData.append(l.branch.branch_code)
#                singleLoanData.append(l.branch.branch_name)
#                singleLoanData.append(l.application.amortization_type)
#                if l.product:
#                     singleLoanData.append(l.product.product_name)
#                else:
#                     singleLoanData.append("")
#                singleLoanData.append(l.tenure)
#                singleLoanData.append(l.intrest_rate)
#                singleLoanData.append(l.processing_fee)
#                singleLoanData.append(l.application.processing_fee_percent)
#                singleLoanData.append(l.penalty)
#                singleLoanData.append(l.stamp_duty)
#                singleLoanData.append(l.ltv)
#                singleLoanData.append(l.lender.lender_name)
#                singleLoanData.append(l.loan_amount)
#                singleLoanData.append(l.loan_type)
#                singleLoanData.append(l.days_past_dues)
#                singleLoanData.append(l.purpose_of_loan)
#                singleLoanData.append(l.total_goods_price)
#                singleLoanData.append(l.total_weight)
#                singleLoanData.append(l.net_weight)
#                singleLoanData.append(l.Originatedby.first_name +" "+ l.Originatedby.last_name)
#                if l.appraisedBy:
#                     singleLoanData.append(l.appraisedBy.first_name +" " +l.appraisedBy.last_name)
#                else:
#                     singleLoanData.append("")
#                singleLoanData.append(l.gst)
#                singleLoanData.append(l.gold_rate_per_gram)
#                if l.disbursed_date:
#                     singleLoanData.append(str(l.disbursed_date))
#                else:
#                     singleLoanData.append("")

#                singleLoanData.append(l.interest_accrued_till_date)
#                singleLoanData.append(l.principal_paid)
#                singleLoanData.append(l.interest_paid)
#                singleLoanData.append(l.principal_remaining)
#                singleLoanData.append(l.interest_remaining)
               

#                loansData.append(singleLoanData)

#           return loansData


     def get_loans_data(self, query_options):
          query_options_available = ['start_date', 'end_date', 'status', 'amortization_type', 'product_name',
                               'product_id', 'tenure__gte', 'tenure__lte', 'lender_name', 'loan_amount_range__gte',
                               'loan_amount_range__lte', 'loan_type', 'purpose_of_loan', 'total_weight',
                               'total_weight__min', 'total_weight__max', 'net_weight', 'net_weight__min',
                               'net_weight__max', 'originated_by', 'disbursed_date']

          filter_query = {}
          queries = []

          for option in query_options_available:
               value = query_options.get(option)
               if value is not None:
                    if option in ['product_name', 'product_id', 'lender_name', 'originated_by', 'purpose_of_loan']:
                         value = value.split(',')
                    if option in ['tenure__gte', 'tenure__lte', 'total_weight__min', 'total_weight__max',
                                   'net_weight__min', 'net_weight__max']:
                         option = option.replace('__', '__' + option.split('__')[1] + '_')
                    queries.append(Q(**{option: value}))


          loans = Loan.objects.filter(**filter_query   ).prefetch_related(
               'application__account__bankaccount_account'
          )

          loans_data = []

          for loan in loans:
               bank_details = loan.application.account.bankaccount_account.all().first()

               single_loan_data = [
                    loan.loan_number,
                    loan.status,
                    loan.application.account.user.get_full_name(),
                    loan.application.account.email,
                    loan.application.account.gender,
                    loan.application.account.year_of_birth.strftime("%d/%m/%Y ,%H:%M"),
                    loan.application.account.user.phone,
                    loan.application.account.occupation,
                    loan.application.account.net_annual_income,
                    loan.application.account.aadhar_no,
                    loan.application.account.pan_no,
                    loan.application.account.mother_name,
                    loan.application.account.father_name,
                    loan.application.account.spouse_name,
                    loan.application.account.education,
                    loan.application.account.religion,
                    loan.application.account.nationality,
                    loan.application.account.disablity,
                    bank_details.bank_name if bank_details else "",
                    bank_details.account_number if bank_details else "",
                    bank_details.ifsc if bank_details else "",
                    bank_details.account_holder_name if bank_details else "",
                    loan.branch.branch_code,
                    loan.branch.branch_name,
                    loan.application.amortization_type,
                    loan.product.product_name if loan.product else "",
                    loan.tenure,
                    loan.intrest_rate,
                    loan.processing_fee,
                    loan.application.processing_fee_percent,
                    loan.penalty,
                    loan.stamp_duty,
                    loan.ltv,
                    loan.lender.lender_name,
                    loan.loan_amount,
                    loan.loan_type,
                    loan.days_past_dues,
                    loan.purpose_of_loan,
                    loan.total_goods_price,
                    loan.total_weight,
                    loan.net_weight,
                    loan.Originatedby.get_full_name(),
                    loan.appraisedBy.get_full_name() if loan.appraisedBy else "",
                    loan.gst,
                    loan.gold_rate_per_gram,
                    str(loan.disbursed_date) if loan.disbursed_date else "",
                    loan.interest_accrued_till_date,
                    loan.principal_paid,
                    loan.interest_paid,
                    loan.principal_remaining,
                    loan.interest_remaining
               ]

               loans_data.append(single_loan_data)

          return loans_data