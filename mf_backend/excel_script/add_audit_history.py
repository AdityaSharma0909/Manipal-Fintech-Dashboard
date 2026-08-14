import traceback
from application.models import Application 
from account.models import Account
from django.db import transaction


class Script:
    account_history = 0
    application_history = 0

    @transaction.atomic
    def add_account_history(self):
        try:
            accounts = Account.objects.all()

            for a in accounts:
                history_instance=a.history.create(
                    history_date=a.created_at,
                    **{field.name: getattr(a, field.name) for field in Account._meta.fields},
                    history_type="+",
                    history_user=a.created_by,
                )
                history_instance.save()
                self.account_history += 1
        except Exception as err:
            print(err)
            traceback.print_exc()

    @transaction.atomic
    def add_application_history(self):
        try:
            applications = Application.objects.all()

            for app in applications:
                history_instance=app.history.create(
                    history_date=app.created_at,
                    history_type="+",
                    history_user=app.Originatedby,
                    **{field.name: getattr(app, field.name) for field in Application._meta.fields},
                )
                history_instance.save()
                self.application_history += 1
        except Exception as err:
            print(err)
            traceback.print_exc()

script = Script()
script.add_account_history()
script.add_application_history()

print(f"Added {script.account_history} account histories.")
print(f"Added {script.application_history} application histories.")

"""
python3 manage.py shell
exec(open('excel_script/add_audit_history.py').read())
"""
