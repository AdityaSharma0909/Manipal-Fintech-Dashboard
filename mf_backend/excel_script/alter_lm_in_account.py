from branch.models import BranchUserMapping
from account.models import Account
from users.models import User

from utils.constants import ROLES

import traceback

class Script:
    updated_accounts = 0
    user_inactive = 0


    def add_account_branch(self):
        try:
            accounts = Account.objects.filter(branch__branch_code='1040031')

            for account in accounts:
                user = User.objects.get(employee_id='00572')
                if account.created_by != user:
                    account.created_by = user
                    account.save()
                    self.updated_accounts += 1

        except Exception as err:
            print(err)
            traceback.print_exc()


    def inactivate_loan_officers(self):
        try:
            branch_user_mappings = BranchUserMapping.objects.filter(branch__branch_code='1040031')
            
            user_ids=branch_user_mappings.values_list('user', flat=True)
            
            users = User.objects.filter(user_id__in=user_ids,role=ROLES.LOAN_OFFICER.value
            ).exclude(employee_id='00572')
                
            for user in users:
                user.is_active = False
                user.save()
                self.user_inactive += 1

        except Exception as err:
            print(err)
            traceback.print_exc()

script = Script()
script.add_account_branch()
script.inactivate_loan_officers()


print(script.updated_accounts)
print(script.user_inactive)


"""
python3 manage.py shell
exec(open('excel_script/alter_lm_in_account.py').read())
"""