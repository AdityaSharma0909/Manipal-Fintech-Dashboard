from django.contrib import admin
from .models import Account, BankAccount, NomineeDetails, InsuranceProduct, NewAccount, AgentAccount, AgentBankAccount
from simple_history.admin import SimpleHistoryAdmin


# Register your models here.


class AccountAdmin(SimpleHistoryAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Account._meta.fields]
    list_display.remove('aadhar_meta_field')
    ordering = ('-created_at',)
    search_fields = ['account_id','customer_id', 'email', 'aadhar_no', 'pan_no']

admin.site.register(Account,AccountAdmin)

class BankAccountAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in BankAccount._meta.get_fields()]
    list_display = [field.name for field in BankAccount._meta.fields]

admin.site.register(BankAccount,BankAccountAdmin)

class NomineeAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in BankAccount._meta.get_fields()]
    list_display = [field.name for field in NomineeDetails._meta.fields]

admin.site.register(NomineeDetails,NomineeAdmin)

class InsuranceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in InsuranceProduct._meta.fields]

admin.site.register(InsuranceProduct, InsuranceAdmin)

class NewAccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in NewAccount._meta.fields]

admin.site.register(NewAccount, NewAccountAdmin)

class AgentAccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AgentAccount._meta.fields]
    search_fields = ['full_name', 'email', 'aadhar_no', 'pan_no']

admin.site.register(AgentAccount, AgentAccountAdmin)

class AgentBankAccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AgentBankAccount._meta.fields]

admin.site.register(AgentBankAccount, AgentBankAccountAdmin)