from django.contrib import admin
from .models import Document
# Register your models here.

class DocumentAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in BankAccount._meta.get_fields()]
    # list_display = [field.name for field in Document._meta.fields]
    search_fields = ['document_id', 'account__account_id', 'document_type']
    list_display = ['document_id','account','document_type', 'file_name', 'file', "created_at"]


admin.site.register(Document, DocumentAdmin)



