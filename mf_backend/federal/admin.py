from django.contrib import admin
from .models import FederalBankApplication,SolidMapping,StateCode,CityCode


# Register your models here.

    
class FederalBankApplicationAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = [field.name for field in FederalBankApplication._meta.fields]

    fields=[field.name for field in FederalBankApplication._meta.fields]
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in obj._meta.fields if not f.editable]
   
    #readonly_fields=['federal_application_id','ddupe_flag','kyc_flag','kyc_profile_flag','partial_kyc_flag','dob_flag','mobile_flag','nri_flag','minor_flag',
    #                 'ddupe_reference_id','aadhar_rrn','reserve_field1','reserve_field2','reserve_field3','reserve_field4','reserve_field5','reserve_field6','reserve_field7',
    #                 'reserve_field8','reserve_field9','reserve_field10']
admin.site.register(FederalBankApplication,FederalBankApplicationAdmin)
admin.site.register(SolidMapping)
admin.site.register(StateCode)
admin.site.register(CityCode)

