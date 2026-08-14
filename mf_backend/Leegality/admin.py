from django.contrib import admin
from .models import LeegalityDocument, Invitee

class InviteeInline(admin.TabularInline):
    model = Invitee
    extra = 0
    fields = ("name", "email", "phone", "sign_url", "active", "expiry_date")


@admin.register(LeegalityDocument)
class LeegalityDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "document_id",
        "user",
        "profile_id",
        "irn",
        "status",
        "is_verified",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "is_verified", "created_at")
    search_fields = ("document_id", "irn", "profile_id", "user__phone", "user__email")
    inlines = [InviteeInline]


@admin.register(Invitee)
class InviteeAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "document", "active", "expiry_date")
    list_filter = ("active",)
    search_fields = ("name", "email", "phone", "document__document_id")
