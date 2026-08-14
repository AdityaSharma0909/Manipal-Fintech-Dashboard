from django.contrib import admin

# Register your models here.
from .models import TeleVerification , Videokyc
class tele_verificationAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in TeleVerification._meta.fields]
admin.site.register(TeleVerification,tele_verificationAdmin)

class VideokycAdmin(admin.ModelAdmin):
    # list_display = [field.name for field in Account._meta.get_fields()]
    list_display = [field.name for field in Videokyc._meta.fields]
admin.site.register(Videokyc,VideokycAdmin)