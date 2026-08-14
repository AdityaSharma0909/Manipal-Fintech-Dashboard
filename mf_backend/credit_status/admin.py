from django.contrib import admin
from credit_status.models import CreditStatus
# Register your models here.
class CreditStatusAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in CreditStatus._meta.fields]
    

admin.site.register(CreditStatus,CreditStatusAdmin)