from application.service import ApplicationService
from utility.crud_helper import CrudHelper
from utils.constants import APPLICATION_STATUS, ApplicationType

"""
    The below class is a helper class for Loan take over flow
    

"""

class LoanTakeOverHelper(CrudHelper):

    def __init__(self, serializer):
        super().__init__(serializer)


    def create_take_over_payload(self, data):
        take_over_data=data.copy()
        take_over_data['lender_name']=take_over_data.pop('take_over_lender')
        take_over_data['gold_weight_pledged']=take_over_data.pop('total_weight')
        take_over_data['requested_amount_from_radian']=take_over_data.pop("take_over_requested_amount_from_radian")
        take_over_data['total_release_amount']=take_over_data.pop("take_over_total_release_amount")
        take_over_data['loan_start_date']=take_over_data.pop('take_over_loan_start_date')
        take_over_data['maturity_date']=take_over_data.pop("take_over_loan_maturity_date")
        take_over_data['loan_reference_number']=take_over_data.pop( "take_over_loan_reference_number")
        return take_over_data



    def create_app_payload(self, data,id):
        application_data=data.copy()
        application_data.pop('loan_amount')
        application_data.pop('tenure')
        application_data.pop('interest_rate')
        application_data["application_number"] = ApplicationService().generate_application_number()
        application_data['status'] = APPLICATION_STATUS.TAKE_OVER_LOAN_INITIATED.value
        application_data['account'] = id
        application_data['application_type']=ApplicationType.TAKEOVER.value
        return application_data


