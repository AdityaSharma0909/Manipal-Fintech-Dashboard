from django.contrib import admin

# Register your models here.
from branch.models import Branch,BranchProductMapping,BranchUserMapping, StampDutyCharges

# Register your models here.
class BranchAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Branch._meta.fields]
    

admin.site.register(Branch,BranchAdmin)


class StampDutyChargesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in StampDutyCharges._meta.fields]
admin.site.register(StampDutyCharges,StampDutyChargesAdmin)


class BranchUserMappingAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in BranchUserMapping._meta.fields]
    

admin.site.register(BranchUserMapping,BranchUserMappingAdmin)

class BranBranchProductMappingAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in BranchProductMapping._meta.fields]
    

admin.site.register(BranchProductMapping,BranBranchProductMappingAdmin)