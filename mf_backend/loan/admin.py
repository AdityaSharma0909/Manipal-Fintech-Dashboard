from django.contrib import admin

from .models import Loan, LoanEMISchedule, LoanEMIRecord, LiveTracking, LoanPaymentTransaction, LoanTakeOver, \
    DemandGeneration, OtherLenderApprainsal, TakeOverResidenceAddress, GprsPhotos
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
class LoanAdmin(SimpleHistoryAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Loan._meta.fields]
    ordering = ('-modified_at',)
    search_fields = ['loan_id','application','loan_number','status', 'loan_amount']

admin.site.register(Loan,LoanAdmin)

class LoanEMIHeaderAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in LoanEMISchedule._meta.fields]
    

admin.site.register(LoanEMISchedule, LoanEMIHeaderAdmin)

class LoanEMIRecordAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in LoanEMIRecord._meta.fields]
    

admin.site.register(LoanEMIRecord,LoanEMIRecordAdmin)

class LiveTrackingAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in LiveTracking._meta.fields]
    

@admin.register(LoanPaymentTransaction)
class LoanPaymentTransaction(admin.ModelAdmin):
    list_display = [field.name for field in LoanPaymentTransaction._meta.fields]

@admin.register(LoanTakeOver)
class LoanTakeOverPanel(admin.ModelAdmin):
    list_display = [field.name for field in LoanTakeOver._meta.fields]
admin.site.register(LiveTracking,LiveTrackingAdmin)

@admin.register(DemandGeneration)
class DemandGenerationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DemandGeneration._meta.fields]



@admin.register(OtherLenderApprainsal)
class OtherLenderApprainsalAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OtherLenderApprainsal._meta.fields]


@admin.register(TakeOverResidenceAddress)
class TakeOverResidenceAddressAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TakeOverResidenceAddress._meta.fields]

@admin.register(GprsPhotos)
class GprsPhotosAdmin(admin.ModelAdmin):
    list_display = [field.name for field in GprsPhotos._meta.fields]