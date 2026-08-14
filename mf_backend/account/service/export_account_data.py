from account.models import Account

class ExportAccountService():

    def get_account_data(self,query_options={}):
        query_options_available = ['account_id__in', 'customer_id__in', 'created_at__gte', 'created_at__lte', 'status', 'branch',
                                   'occupation', 'net_annual_income__gte' , 'net_annual_income__lte', 'aadhar_no', 'pan_no',
                                   'insurance_amount__gte', 'insurance_amount__lte']
        
        filter_query = {}
        if len(query_options)>0:
            for i in query_options_available:
                opt = query_options.get(i)
                if opt is not None:
                        if i =='account_id__in':
                            opt=opt.split(",")
                        filter_query[i] = opt
        
        accounts = Account.objects.filter(**filter_query).prefetch_related(
            'bankaccount_account',
            'nomieedetails_account',
        )

        accountData = []

        for account in accounts:
            bank_details = account.bankaccount_account.all().first()
            nominee_details = account.nomieedetails_account.all().first()
            single_account_data = [
                account.user.get_full_name(),
                account.customer_id,
                account.email,
                account.gender,
                account.year_of_birth.strftime("%d/%m/%Y"),
                account.occupation,
                account.sub_occupation,
                account.profile_photo,
                account.net_annual_income,
                account.aadhar_no,
                account.pan_no,
                account.mother_name,
                account.father_name,
                account.spouse_name,
                account.education,
                account.religion,
                account.disablity,
                account.nationality,
                account.caste,
                account.maritial_status,
                account.status,
                bank_details.bank_name if bank_details else "",
                bank_details.account_number if bank_details else "",
                bank_details.ifsc if bank_details else "",
                bank_details.account_holder_name if bank_details else "",
                account.branch.branch_code if account.branch else "",
                account.branch.branch_name if account.branch else "",
                account.branch.state if account.branch else "",
                nominee_details.first_name+" "+nominee_details.last_name if nominee_details else "",
                nominee_details.age if nominee_details else "",
                nominee_details.relation if nominee_details else "",
                nominee_details.contact_no if nominee_details else "",
                account.insurance_product.product_name if account.insurance_product else "",  
                account.insurance_product.company_name if account.insurance_product else "",  
                account.insurance_product.validity if account.insurance_product else "",
                account.insurance_product.coverage if account.insurance_product else "",  
                account.insurance_product.price if account.insurance_product else "",
                account.created_at.strftime('%d/%m/%Y, %H:%M'),
            ]

            accountData.append(single_account_data)

        return accountData