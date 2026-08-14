from urllib import request
from application.serializers import ApplicationModelSerializer

from utils.constants import APPLICATION_STATUS, APPROVED , ROLES , REJECTED , ON_HOLD , DEVIATED
from utils.sms import SMSService
from utils.envSetup import environment


class ApplicationApproveLogic:

    # def approve_application(self, approved_by, application, response, comment, response_status):
    #     template=''
    #     if response == APPROVED:
    #         template='application_approved'
    #         application.status = self.__change_new_loan_to_approved(application)
    #     elif response=='ROLL_BACK':
    #         template='application_roll_back'
    #         application.status=APPLICATION_STATUS.ROLL_BACK_BY_CPC.value
    #         application.rejection_status=response_status
    #         application.kick_back_comment=comment
    #     else:
    #         template='application_rejected'
    #         application.status = APPLICATION_STATUS.APPLICATION_REJECTED_BY_CPC.value
    #         application.cpc_comment = comment
    #     application.approvedByCPC = approved_by
    #     application.save()
    #     SMSService().send_status_update(template=template,
    #                                     mobile=str(application.Originatedby.phone),
    #                                     application_no=application.application_number,
    #                                     customer_name=application.account.user.get_full_name()
    #                                     )
    #     return ApplicationModelSerializer(application).data

    def approve_application(self, approved_by, application, response, comment, response_status, loan_amount=None, deviated_amount=None):
        template = ''
        
        # Check if the approver's role is CPC
        if approved_by.role == ROLES.CPC.value:
            if response == 'APPROVED':
                template = 'application_approved'
                # Change the application status to approved
                application.status = self.__change_new_loan_to_approved(application)

            elif response == 'ROLL_BACK':
                template = 'application_roll_back'
                # Set the application status to roll back by CPC
                application.status = APPLICATION_STATUS.ROLL_BACK_BY_CPC.value
                application.rejection_status = response_status
                application.kick_back_comment = comment

            else:  # Assuming the only other response is 'REJECTED'
                template = 'application_rejected'
                # Set the application status to rejected by CPC
                application.status = APPLICATION_STATUS.APPLICATION_REJECTED_BY_CPC.value
                application.cpc_comment = comment
            # Set the approvedByCPC attribute to the current approver
            application.approvedByCPC = approved_by

        # Check if the approver's role is Credit Manager
        elif approved_by.role == ROLES.CREDIT_MANAGER.value :
            if response == 'APPROVED':
                template = 'application_approved'

                if not (application.product.minimum_ticket_size <= loan_amount <= application.product.maximum_ticket_size):
                    return {
                        "status": "error",
                        "message": "Loan amount must be between the minimum and maximum ticket size of the product.",
                    }
                
                # Change the application status to generate loan document
                application.status = APPLICATION_STATUS.GENERATE_LOAN_DOCUMENT.value
                application.approvalActionCM = APPROVED
                application.cm_comment = comment
                application.loan_amount = loan_amount
                application.processing_fee=float(application.product.processing_fee)*(application.loan_amount)/100
                application.current_gst_rate = float(environment.CURRENT_GTS_RATE)
                application.gst = (application.current_gst_rate/100) * application.processing_fee
                sum_assured = loan_amount if loan_amount <= 200000 else 200000
                insurance_deduction = (application.insurance_product.rate * sum_assured) / 1000
                application.insurance_amount_deducted = insurance_deduction
                disbursal_amount = float(application.loan_amount) - float(application.processing_fee) - float(application.gst) - float(application.insurance_amount_deducted)
                application.disbursal_amount=disbursal_amount
                application.net_disbursed_amount=disbursal_amount

            elif response == 'ROLL_BACK':
                template = 'application_roll_back'
                # Set the application status to roll back by CM
                application.status = APPLICATION_STATUS.ROLL_BACK_BY_CM.value
                application.rejection_status = response_status
                application.kick_back_comment = comment

            elif response == 'DEVIATE':
                if not (application.product.minimum_ticket_size <= loan_amount <= application.product.maximum_ticket_size):
                    return {
                        "status": "error",
                        "message": "Loan amount must be between the minimum and maximum ticket size of the product.",
                    }

                # Change the application status to sent to Business Head
                application.status = APPLICATION_STATUS.APPLICATION_SENT_TO_BH.value
                application.loan_amount = loan_amount
                application.deviated_amount = deviated_amount
                application.cm_comment = comment
                application.approvalActionCM = DEVIATED

            else:  # Assuming the only other response is 'REJECTED'
                template = 'application_rejected'
                # Change the application status to rejected by CM
                application.status = APPLICATION_STATUS.APPLICATION_REJECTED_BY_CM.value
                application.cm_comment = comment
                application.approvalActionCM = REJECTED
            # Set the approvedByCM attribute to the current approver
            application.approvedByCM = approved_by

        # Check if the approver's role is Business Head
        elif approved_by.role == ROLES.BUSINESS_HEAD.value and application.status == APPLICATION_STATUS.APPLICATION_SENT_TO_BH.value:
            if response == 'APPROVED':
                template = 'application_approved'
                if not (application.product.minimum_ticket_size <= loan_amount <= application.product.maximum_ticket_size):
                    return {
                        "status": "error",
                        "message": "Loan amount must be between the minimum and maximum ticket size of the product.",
                    }
                
                final_amount=loan_amount+deviated_amount
                if not (application.product.minimum_ticket_size <= final_amount <= application.product.maximum_ticket_size):
                    return {
                        "status": "error",
                        "message": "Loan amount must be between the minimum and maximum ticket size of the product.",
                    }
                
                # Change the application status to sent back by Business Head
                application.status = APPLICATION_STATUS.APPLICATION_SENT_BACK_BY_BH.value
                application.approvalActionBH = APPROVED
                application.loan_amount = final_amount
                application.deviated_amount = deviated_amount
                application.bh_comment = comment
            else:  # Assuming the only other response is 'REJECTED'
                # Change the application status to sent back by Business Head
                template = 'application_rejected'
                if not (application.product.minimum_ticket_size <= loan_amount <= application.product.maximum_ticket_size):
                    return {
                        "status": "error",
                        "message": "Loan amount must be between the minimum and maximum ticket size of the product.",
                    }
                application.status = APPLICATION_STATUS.APPLICATION_SENT_BACK_BY_BH.value
                application.bh_comment = comment
                application.approvalActionBH = REJECTED
                application.loan_amount = loan_amount
                application.deviated_amount = deviated_amount
            # Set the approvedByBH attribute to the current approver
            application.approvedByBH = approved_by

        # Save the changes to the application
        application.save()
        
        # Send status update SMS if the response is not 'DEVIATE'
        if response != 'DEVIATE' and approved_by.role != ROLES.BUSINESS_HEAD.value:
                SMSService().send_status_update(
                    template=template,
                    mobile=str(application.Originatedby.phone),
                    application_no=application.application_number,
                    customer_name=application.account.user.get_full_name()
                )
    
        # Return serialized application data
        return ApplicationModelSerializer(application).data



    def __change_new_loan_to_approved(self, application):
        if application.product:
            return APPLICATION_STATUS.GENERATE_LOAN_DOCUMENT.value
        else:
            return APPLICATION_STATUS.TAKE_OVER_APPROVED.value

    def __take_over_loan_approved(self):
        return APPLICATION_STATUS.TAKE_OVER_APPROVED.value
