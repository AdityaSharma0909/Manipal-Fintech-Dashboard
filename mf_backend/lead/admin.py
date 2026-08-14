from django.contrib import admin
from .models import Lead , LeadDocument, NewLead

# Register your models here.


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Lead._meta.fields]
    search_fields = [
        "first_name",
        "last_name",
        "lead_type",
        "phone",
        "email",
        "source",
    ]

class LeadDocumentAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in LeadDocument._meta.fields]
    

admin.site.register(LeadDocument, LeadDocumentAdmin)

class NewLeadAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in NewLead._meta.fields]
    search_fields = [
        "full_name",
        "phone",
        "email",
        "source",
    ]


admin.site.register(NewLead, NewLeadAdmin)