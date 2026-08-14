from django.contrib import admin
from cibil_score.models import CibilScore
# Register your models here.
class CibilScoreAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in CibilScore._meta.fields]
    

admin.site.register(CibilScore,CibilScoreAdmin)
