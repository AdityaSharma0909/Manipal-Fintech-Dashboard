from application.models import Application
from utils.constants import ROLES
from phonenumbers import PhoneNumber 

class ExportCamService():

    def get_cam_data(self, request):
        application = Application.objects.get(application_id=request.GET.get("application_id"))
        address = application.account.user_addresse.all().first()
        credit_status = application.account.creditstatus_account.all().first()
        reference_pds = application.account.refenrence_pd_account.all()
        bank_details = application.account.bankaccount_account.all().first()
        nominee_details = application.account.nomieedetails_account.all().first()
        score_me_details = application.score_me_application.all().first()
        pd_tele_data = application.tele_application if hasattr(application, 'tele_application') else None
        credit_score = application.cibil_score_application.all().first()

        def format_phone_number(phone_number):
            if isinstance(phone_number, PhoneNumber):
                return f"+{phone_number.country_code}{phone_number.national_number}"
            return str(phone_number)
        
        base_cam_data = [
            application.account.user.get_full_name(),
            application.account.email,
            format_phone_number(application.account.user.phone),
            f"{address.building_name}, {address.street_name}, {address.city}, {address.state}-{address.pincode}, {address.country}" if address else "",
            application.application_number,
            credit_status.nature_of_business if credit_status else "",
            credit_status.shop_number_of_year if credit_status else "",
            nominee_details.first_name + " " + nominee_details.last_name if nominee_details else "",
        ]

        score_me_data = [
            credit_score.cb_score if credit_score else "",
            credit_score.obligation if credit_score else "",
            score_me_details.cash_flow if score_me_details else "",
            score_me_details.average_monthly_balance if score_me_details else "",
            credit_score.existing_loan_amount if credit_score else "",
            credit_score.emi_of_existing_loan if credit_score else "",
            score_me_details.leverage_to_income if score_me_details else "",
            "",
        ]

        reference_data_list = []
        if reference_pds.exists():
            for reference_pd in reference_pds:
                reference_data = [
                    reference_pd.account.user.get_full_name() if reference_pd else "",
                    reference_pd.enterprise_name if reference_pd else "",
                    reference_pd.residential if reference_pd else "",
                    reference_pd.number_of_years if reference_pd else "",
                    reference_pd.number_of_family_members if reference_pd else "",
                    reference_pd.nature_of_business if reference_pd else "",
                    reference_pd.sub_nature_of_business if reference_pd else "",
                    reference_pd.number_of_earning_members if reference_pd else "",
                    format_phone_number(reference_pd.phone) if reference_pd else "",
                    reference_pd.relation_with_applicant if reference_pd else "",
                ]
                reference_data_list.append(reference_data)
        
        bank_detail_list = [
            bank_details.bank_name if bank_details else "",
            bank_details.account_number if bank_details else "",
            bank_details.ifsc if bank_details else ""
        ]

        credit_data = [
            credit_status.house_ownership if credit_status else "",
            credit_status.house_number_of_year if credit_status else "",
            credit_status.shop_ownership if credit_status else "",
            credit_status.shop_number_of_year if credit_status else "",
            credit_status.nature_of_business if credit_status else "",
            credit_status.monthly_income if credit_status else "",
            credit_status.monthly_expenditure if credit_status else '',
            credit_score.no_of_loans_running if credit_score else "",
            credit_score.no_of_loans_closed_in_last_1_year if credit_score else "",
            credit_score.any_loan_applied_in_last_30_days if credit_score else "",
            credit_status.account_held_for_no_of_years if credit_status else "",
            credit_status.fixed_assets_held_by_him_and_family if credit_status else "",
        ]

        luc_data = [
            application.purpose_of_loan,
            application.requested_loan_amount,
            application.expected_income_increase,
            application.verify_the_usage
        ]

        pd_tele_data = [
            pd_tele_data.report_in_brief if pd_tele_data else "",
            application.Originatedby.get_full_name() if application else "",
            pd_tele_data.created_by.get_full_name() if pd_tele_data else "",
            pd_tele_data.location_captured if pd_tele_data else "",
            pd_tele_data.picture_captured if pd_tele_data else "",
            pd_tele_data.observation if pd_tele_data else "",
            pd_tele_data.observation_comment if pd_tele_data else "",
            pd_tele_data.residential_stability if pd_tele_data else "",
            pd_tele_data.residential_stability_comment if pd_tele_data else "",
            pd_tele_data.business_stability if pd_tele_data else "",
            pd_tele_data.business_stability_comment if pd_tele_data else "",
            pd_tele_data.no_of_similar_business if pd_tele_data else "",
            pd_tele_data.external_income if pd_tele_data else "",
            pd_tele_data.suppliers_customer_feeedback if pd_tele_data else "",
        ]

        policy_deviation_data=[
            application.product.product_name,
            application.eligible_amount,
            application.deviated_amount,
            application.approvedByCM.get_full_name() if application.approvedByCM else "",
            application.approvedByBH.get_full_name() if application.approvedByBH else "",
            application.bh_comment if application.bh_comment else "",
            application.cm_comment if application.cm_comment else "",
        ]

        disbursement_note_data = [
            application.account.user.get_full_name(),
            application.Originatedby.get_full_name(),
            application.approvedByBH.get_full_name() if application.approvedByBH else "",
            application.product.product_name,
            application.deviated_amount,
            application.approvalActionBH,
            application.loan_amount,
            application.product.tenure,
            application.processing_fee,
            "",
            "",
            application.disbursal_amount,
            bank_details.account_number if bank_details else "",
            bank_details.ifsc if bank_details else "",
            'YES' if bank_details and bank_details.verified else 'NO',
            "",
            bank_details.bank_name if bank_details else "",
            bank_details.branch_name if bank_details else "",
            application.branch.branch_name,
            "CPC Team",
            application.approvedByCM.get_full_name() if application.approvedByCM else "",
            "CPC Team",
            "Lavanya Byanna",
        ]
        
        return base_cam_data, reference_data_list, credit_data, bank_detail_list , luc_data , score_me_data , pd_tele_data , policy_deviation_data , disbursement_note_data

        