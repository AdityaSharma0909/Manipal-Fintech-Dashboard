from django.contrib import admin
from .models import  Application, ApplicationGoodsMapping, ApplicationOtp , ApplicationDocument, NewApplication
from .models import AssetDocuments, LoanDocument
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.


class ApplicationAdmin(SimpleHistoryAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Application._meta.fields]
    ordering = ('-created_at',)
    search_fields = ['application_id', 'application_number', 'account__customer_id', 'account__account_id', 'account__user__first_name', 'account__user__last_name', 'account__aadhar_no', 'account__pan_no',]

admin.site.register(Application,ApplicationAdmin)

class ApplicationGoodsMappingAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in ApplicationGoodsMapping._meta.fields]
admin.site.register(ApplicationGoodsMapping,ApplicationGoodsMappingAdmin)


class ApplicationOtpAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in ApplicationOtp._meta.fields]
admin.site.register(ApplicationOtp,ApplicationOtpAdmin)


class AssetDocumentAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in BankAccount._meta.get_fields()]
    # list_display = [field.name for field in Document._meta.fields]
    list_display = ['asset_document_id', 'asset_document_type', 'asset']

admin.site.register(AssetDocuments, AssetDocumentAdmin)


class LoanDocumentAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in BankAccount._meta.get_fields()]
    # list_display = [field.name for field in Document._meta.fields]
    list_display = [field.name for field in LoanDocument._meta.fields]
    search_fields = ["application__application_id"]
    # list_display = ['document_id', 'document_type', 'file_name', 'file']

admin.site.register(LoanDocument, LoanDocumentAdmin)

class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ApplicationDocument._meta.fields]

admin.site.register(ApplicationDocument, ApplicationDocumentAdmin)


class NewApplicationAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in BankAccount._meta.get_fields()]
    list_display = [field.name for field in NewApplication._meta.fields]

admin.site.register(NewApplication, NewApplicationAdmin)
