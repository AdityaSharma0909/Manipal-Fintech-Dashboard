from account.models import Account
from loan.models import Loan
from users.models import Address
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.constants import ADDRESS_TYPE
from disbursements.models import Disbursement
from django.db.models import Max

import pytz


class ExportInsuranceService():

    def exportInsurance(self, request):
            
        accounts = Account.objects.all()
        loans = Loan.objects.all()
        addresses = Address.objects.all()
        insuranceData = []

        account= Account.objects.filter(insurance_product__isnull=False, insurance_amount_covered_from__isnull=False)

        for a in account:
                
            singleInsuranceData = []
            singleInsuranceData.append('')
            singleInsuranceData.append(a.customer_id)
            name = a.user.first_name + " " + a.user.last_name
            singleInsuranceData.append(name)
            singleInsuranceData.append(a.branch.branch_name)
            singleInsuranceData.append(a.branch.branch_code)
            # singleInsuranceData.append("")  # Disbursement Date
            latest_disbursement = Disbursement.objects.filter(application=a.insurance_amount_covered_from).aggregate(latest_date=Max('disbursal_date'))
            if latest_disbursement['latest_date']:
                disbursement_date = latest_disbursement['latest_date'].strftime("%d/%m/%Y")
            else:
                disbursement_date=""
            singleInsuranceData.append(disbursement_date)
            singleInsuranceData.append("")  # Ploicy Start Date
            singleInsuranceData.append("")  # Ploicy End Date

            if '1' in a.insurance_product.coverage:
                numberOfApplicant = 1
            elif '2' in a.insurance_product.coverage:
                numberOfApplicant = 2
            else:
                numberOfApplicant = None
            singleInsuranceData.append(numberOfApplicant)  # Number of Applicant

            singleInsuranceData.append(1)   # Loan Tenure
            singleInsuranceData.append(a.insurance_amount_covered_from.loan_amount)
            singleInsuranceData.append('') # Policy Tenure (In Years)
            singleInsuranceData.append(name)
            singleInsuranceData.append(a.year_of_birth.strftime("%d/%m/%Y"))
            age = relativedelta(datetime.now(tz=pytz.utc), a.year_of_birth).years
            singleInsuranceData.append(age)
            singleInsuranceData.append(a.gender)
            permanentAddress = a.user_addresse.filter(address_type=ADDRESS_TYPE.PERMANENT_ADDRESS.value).first()
            if permanentAddress:
                singleInsuranceData.append(permanentAddress.building_name +", "+permanentAddress.street_name)
                singleInsuranceData.append(permanentAddress.city)
                singleInsuranceData.append(permanentAddress.city)
                singleInsuranceData.append(permanentAddress.state)
                singleInsuranceData.append(permanentAddress.pincode)
            else:
                singleInsuranceData.extend([''] * 5)
            singleInsuranceData.append(a.user.phone)
            singleInsuranceData.append(a.email)
            singleInsuranceData.append('')
            nominee = a.nomieedetails_account.all().first()
            if nominee:
                singleInsuranceData.append(nominee.first_name +" "+nominee.last_name)
                singleInsuranceData.append(nominee.age)
                singleInsuranceData.append(nominee.relation)
            else:
                singleInsuranceData.extend([''] * 3)


            singleInsuranceData.append('') # SM Name
            singleInsuranceData.append('') # Premium Amount
            singleInsuranceData.append('') # GST
            singleInsuranceData.append(a.insurance_product.price) # Total
            singleInsuranceData.append('') # UTR No.
            singleInsuranceData.append('') # UTR Amount
            singleInsuranceData.append('') # UTR Date
            singleInsuranceData.append(a.insurance_product.coverage) # Product

            insuranceData.append(singleInsuranceData)
        
        return insuranceData

