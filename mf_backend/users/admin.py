from django.contrib import admin
from .models import User ,UserOtp,  VerificationToken
from django.contrib.auth.admin import UserAdmin 
from .models import Address, UserDeviceDetails ,TimeStamp, UserReward
from branch.models import BranchUserMapping
from users.selfie_urls import get_selfie_access_url

class BranchUserMappingInline(admin.TabularInline):  
    model = BranchUserMapping
    extra = 1
# Now register the new UserAdmin...
@admin.register(User)
class UserAdmin(UserAdmin):


    list_display = ['username', 'email', 'role', 'phone', 'first_name', 'last_name', 'date_of_joining', 'exclude_from_bt_date_logic', 'aadhar_no', 'pan_no', 'entity_id','pincode','is_active','employee_profile_photo', 'assign_so']
    list_filter = ['role', 'exclude_from_bt_date_logic', 'is_active']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name', 'aadhar_no', 'pan_no', 'role']

    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': ('phone','role',"aadhar_no","pan_no","entity_id","designation","employee_id","date_of_joining",'employee_profile_photo','state', 'district', 'city', 'pincode', 'team', 'badge', 'assign_so')
        }),
        ('BT Lead Eligibility', {
            'fields': ('exclude_from_bt_date_logic',),
            'description': 'Enable this to allow the Sales Officer to create BT leads before completing 60 days.',
        }),
    ) 
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2')}
        ),
    )
    inlines = [BranchUserMappingInline]

    def save_model(self, request, obj, form, change):
        # Prevent deactivation of super admin
        if 'is_active' in form.changed_data and not obj.is_active and obj.role == 'SUPER_ADMIN':
            from django.core.exceptions import ValidationError
            raise ValidationError("Super admin cannot be deactivated.")
        super().save_model(request, obj, form, change)

@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserReward._meta.fields]

@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    list_display = [field.name for field in VerificationToken._meta.fields]

@admin.register(UserOtp)
class UserOtpAdmin(admin.ModelAdmin):
    list_display = ('secret_key', 'user' )


class AddressesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Address._meta.fields]

@admin.register(UserDeviceDetails)
class UserDeviceDetailsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserDeviceDetails._meta.fields]

admin.site.register(Address,AddressesAdmin)

from django.utils.safestring import mark_safe


class TimeStampAdmin(admin.ModelAdmin):
    list_display = ("timestamp_id", "user", "status", "latitude", "longitude", "selfie_display", "remarks", "created_at")
    search_fields = (
        "timestamp_id",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__phone",
        "status",
        "remarks",
    )

    def selfie_display(self, obj):
        if obj.selfie:
            try:
                selfie_url = get_selfie_access_url(obj.selfie)
                if selfie_url:
                    return mark_safe(f'<a href="{selfie_url}" target="_blank">View Selfie</a>')
                return mark_safe(f'<a href="{obj.selfie.url}" target="_blank">View Selfie</a>')
            except Exception as e:
                return f"Error: {str(e)}"
        return "No Selfie"
    
    selfie_display.short_description = "Selfie"

admin.site.register(TimeStamp,TimeStampAdmin)
