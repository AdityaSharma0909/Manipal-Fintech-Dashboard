from django.db.models import Q, F, Value
from django.db.models.functions import Concat

from disbursements.models import Disbursement
from disbursements.service.logic.disburse_logics import DisburseLoan


class DisbursementHelper:



    def disburse_loan(self, data, user):
        return DisburseLoan().process(data=data, user=user)


    def get_pending_disbursals(self, filters):
        query={}
        filter_options=['payment_mode',
                        'disbursal_date',
                        'disbursal_date__gte',
                        'disbursal_date__lte']
        query['utr_no__isnull']=filters.get('disbursement_status','completed')=='pending'

        for i in filter_options:
            opt=filters.get(i)
            if opt is not None:
                if i.startswith('disbursal_date'):
                    query[i.replace('disbursal_date','disbursal_date')]=opt
                else:
                    query[i]=opt
        data=list(Disbursement.objects.filter(Q(**query)).values('utr_no',"disbursement_id",
                                                                        'payment_mode',
                                                                        'disbursal_date',
                                                                        'disbursement_status',
                                                                        'disbursement_amount',
                                                                        'payment_status',
                                                                ).annotate(
                    application_number=F('application__application_number'),
                    application_id=F('application__application_id'),
                    loan_id=F('loan__loan_id'),
                    loan_amount=F('loan__loan_amount'),
                    loan_number=F('loan__loan_number'),
                    name=Concat(F('application__account__user__first_name'), Value(' '),
                                F('application__account__user__last_name')),
                    created_at=F('created_at'),
                    modified_at=F('modified_at'),
                ).order_by('-modified_at'))
        return data