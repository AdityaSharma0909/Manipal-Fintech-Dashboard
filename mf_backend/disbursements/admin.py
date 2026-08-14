from django.contrib import admin

# Register your models here.
from .models import Disbursement

# Register your models here.
class DisbursementAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Disbursement._meta.fields]
    

admin.site.register(Disbursement,DisbursementAdmin)