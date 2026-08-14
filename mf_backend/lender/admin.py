from django.contrib import admin

# Register your models here.

from .models import Lender,LenderBranchMapping,LenderBranch

# Register your models here.
class LenderAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Lender._meta.fields]
    

admin.site.register(Lender,LenderAdmin)

class LenderBranchAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in LenderBranch._meta.fields]
    

admin.site.register(LenderBranch,LenderBranchAdmin)

class LenderBranchMappingAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in LenderBranchMapping._meta.fields]
    

admin.site.register(LenderBranchMapping,LenderBranchMappingAdmin)