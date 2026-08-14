from branch.models import BranchUserMapping
from application.models import Application
# a = Application.objects.filter(branch__isnull=True).count()
# print(a)

from loan.models import Loan

import traceback

# script to add data in branch field of application and loan
class Script():
    application_branch = 0
    loan_branch = 0 


    def add_application_branch(self):
        try:
            # Retrieve all applications
            applications = Application.objects.all()

            # Iterate through all applications
            for application in applications:
                # Get the originated_by value from the current application
                originated_by = application.Originatedby
                branch_user = BranchUserMapping.objects.filter(
                    user=originated_by
                )

                if len(branch_user) > 0: 
                    application.branch = branch_user[0].branch
                    application.save()
                    self.application_branch += + 1

        except Exception as err:
            print(err)
            traceback.print_exc()




    def add_loan_branch(self):
        try:
            # Retrieve all applications
            loans = Loan.objects.all()

            # Iterate through all applications
            for loan in loans:
                # Get the originated_by value from the current application
                originated_by = loan.Originatedby
                branch_user = BranchUserMapping.objects.filter(
                    user=originated_by
                )

                if len(branch_user) > 0: 
                    loan.branch = branch_user[0].branch
                    loan.save()
                    self.loan_branch += + 1


        except Exception as err:
            print(err)
            traceback.print_exc()

script = Script()
script.add_application_branch()
script.add_loan_branch()


print(script.application_branch)
print(script.loan_branch)


"""
python3 manage.py shell
exec(open('excel_script/add_branch.py').read())
"""