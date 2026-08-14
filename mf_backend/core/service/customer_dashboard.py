from django.db.models import F

from application.models import Application
from application.serializers import CustomerDashboardSerializer, CustomerApplicationDetailsSerializer
from application.services.application_services import ApplicationHelper
from loan.services.loan_services import LoanHelper
from utility.common_utils import custom_response_obj
from django.core.exceptions import ObjectDoesNotExist


class CustomerData:
    """
            return following things Application ID, Branch details, Product details, Lender details, Loan ID, Loan Amount, Tenure, Days past due, Loan Status, Loan Start date, net weight of asset, Interest accrued till date

        """
    def get_dashboard_data(self, account_id):
        application=Application.objects\
            .filter(account__account_id=account_id).annotate(
            loan_id=F('loan_application__loan_id'),
            days_past_due=F('loan_application__days_past_dues'),
            interest_accrued_till_date=F('loan_application__interest_accrued_till_date'),
            loan_status=F('loan_application__status'),
            loan_number=F('loan_application__loan_number'),
            loan_disbursed_date=F('loan_application__disbursed_date')

        )
        data=CustomerDashboardSerializer(application, many=True).data
        return custom_response_obj(message={"loans": data}, code=200)



    def get_customer_app_details(self, application_id):
        data, application = ApplicationHelper().get_app_overview(application_id)
        
        try:
            loan = application.loan_application.get()
            loan = LoanHelper().get_loan_data(loan.loan_id, loan=loan)
        except ObjectDoesNotExist:
            print("No loan found for this application.")
            loan = {}
        
        data.update(**loan)
        return custom_response_obj(data, 200)

