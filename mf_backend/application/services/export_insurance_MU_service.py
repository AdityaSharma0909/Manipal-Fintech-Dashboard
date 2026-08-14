from application.models import Application
from users.models import Address
from utils.constants import ADDRESS_TYPE , LENDING_TYPE


class ExportMUInsuranceService():
    def exportMUInsurance(self , request):

        application = Application.objects.filter(insurance_product__isnull = False, insurance_product__insurance_policy_type = LENDING_TYPE.MSME_UNSECURED.value)
        insuranceData = []
        for app in application:

            singleInsuranceData = []
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append(app.application_number) #need to be dicussed
            singleInsuranceData.append(app.account.user.first_name)
            singleInsuranceData.append(app.account.user.last_name)
            singleInsuranceData.append(app.account.year_of_birth.strftime("%d/%m/%Y"))
            singleInsuranceData.append(app.account.gender)
            permanentAddress = app.account.user_addresse.filter(address_type=ADDRESS_TYPE.PERMANENT_ADDRESS.value).first()
            if permanentAddress:
                singleInsuranceData.append(permanentAddress.building_name +", "+permanentAddress.street_name)
                singleInsuranceData.append(permanentAddress.city)
                singleInsuranceData.append(permanentAddress.state)
                singleInsuranceData.append(permanentAddress.country)
                singleInsuranceData.append(permanentAddress.pincode)
            else:
                singleInsuranceData.extend([''] * 5)
            singleInsuranceData.append(app.loan_amount)
            singleInsuranceData.append(app.tenure)
            singleInsuranceData.append(app.loan_amount)
            singleInsuranceData.append('')
            singleInsuranceData.append(app.insurance_product.coverage)
            singleInsuranceData.append(app.tenure) 
            singleInsuranceData.append(app.insurance_amount_deducted)
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('level')
            nominee = app.account.nomieedetails_account.all().first()
            if nominee:
                singleInsuranceData.append(nominee.first_name)
                singleInsuranceData.append(nominee.last_name)
                singleInsuranceData.append('') #TO ask
                singleInsuranceData.append('')
                singleInsuranceData.append(nominee.relation)
            else:
                singleInsuranceData.extend([''] * 5)
            singleInsuranceData.append('NO')
            singleInsuranceData.append('YES')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append('')
            singleInsuranceData.append(app.account.user.phone)

            insuranceData.append(singleInsuranceData)
        
        return insuranceData


            
            


            