from django.contrib import admin
from zoop.models import PanVerification, BankVerification, DrivingLicenceVerification, ChequeOCRVerification, OCRLiteVerification, VoterIDAdvanceVerification, PassportAdvanceVerification

# Register your models here.
@admin.register(PanVerification)
class PanVerificationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PanVerification._meta.fields]
    
@admin.register(OCRLiteVerification)
class OCRLiteVerificationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OCRLiteVerification._meta.fields] 
    search_fields = ['id']