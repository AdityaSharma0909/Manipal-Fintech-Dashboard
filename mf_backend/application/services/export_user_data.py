# from application.models import Application 
# from account.models import BankAccount
# from django.db.models import Q

# class ExportUserApplicationService():

#      def export_user_application(self, request):

#         userapplicationdata = []
#         user_details = Application.objects.all()

#         user_account = BankAccount.objects.all()


#         for a, b in zip(user_details, user_account):
            
#             singleuserapplicationData = []
#             singleuserapplicationData.append(a.account.user.first_name +" "+ a.account.user.last_name)
#             singleuserapplicationData.append(a.account.email)
#             singleuserapplicationData.append(a.account.gender)
#             singleuserapplicationData.append(a.account.year_of_birth.strftime("%d/%m/%Y ,%H:%M"))
#             singleuserapplicationData.append(a.account.user.phone)
#             singleuserapplicationData.append(a.account.occupation)
#             singleuserapplicationData.append(a.account.net_annual_income)
#             singleuserapplicationData.append(a.account.aadhar_no)
#             singleuserapplicationData.append(a.account.pan_no)
#             singleuserapplicationData.append(a.account.mother_name)
#             singleuserapplicationData.append(a.account.father_name)
#             singleuserapplicationData.append(a.account.spouse_name)
#             singleuserapplicationData.append(a.account.education)
#             singleuserapplicationData.append(a.account.religion)
#             singleuserapplicationData.append(a.account.nationality)
#             singleuserapplicationData.append(a.account.disablity)
#             singleuserapplicationData.append(b.bank_name)
#             singleuserapplicationData.append(b.account_number)
#             singleuserapplicationData.append(b.ifsc)
#             singleuserapplicationData.append(b.account_holder_name)
#             date_time = a.created_at.strftime("%d/%m/%Y, %H:%M")	
#             singleuserapplicationData.append((date_time))
            
#             userapplicationdata.append(singleuserapplicationData)

#         return userapplicationdata
            

            