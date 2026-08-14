from django.contrib import admin

# Register your models here.
from .models import Reference_PD
# Register your models here.
class ReferencePDAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Reference_PD._meta.fields]
admin.site.register(Reference_PD,ReferencePDAdmin)