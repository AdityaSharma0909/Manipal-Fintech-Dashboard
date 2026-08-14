from branch.models import BranchUserMapping
from account.models import Account

from loan.models import Loan

import traceback


# script to add data in branch field of account and loan
class Script:
    account_branch = 0

    def add_account_branch(self):
        try:
            accounts = Account.objects.all()

            # Iterate through all applications
            for a in accounts:
                # Get the originated_by value from the current application
                created_by = a.created_by
                branch_user = BranchUserMapping.objects.filter(user=created_by)

                if len(branch_user) > 0:
                    a.branch = branch_user[0].branch
                    a.save()
                    self.account_branch += +1

        except Exception as err:
            print(err)
            traceback.print_exc()


script = Script()
script.add_account_branch()

print(script.account_branch)


"""
python3 manage.py shell
exec(open('excel_script/add_branch_in_account.py').read())
"""
