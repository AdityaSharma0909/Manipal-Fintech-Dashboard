from django.contrib import admin
from crif_bureau.models import CrifBureauReportTrace, CrifBureauTrace


@admin.register(CrifBureauTrace)
class CrifBureauTraceAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "pan_number",
        "score",
        "status",
        "reference_number",
        "created_at",
        "modified_at",
    )
    list_filter = ("status", "created_at", "modified_at")
    search_fields = ("phone_number", "pan_number", "reference_number")
    readonly_fields = ("created_at", "modified_at")

    fieldsets = (
        ("Basic Info", {
            "fields": ("phone_number", "pan_number", "score", "status", "reference_number", "pdf_report_link")
        }),
        ("Trace Logs", {
            "fields": (
                "phone_to_pan_request",
                "phone_to_pan_response",
                "consent_request",
                "consent_response",
                "webhook_payload",
                "decrypted_webhook_data",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "modified_at")
        }),
    )


@admin.register(CrifBureauReportTrace)
class CrifBureauReportTraceAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "pan_number",
        "score",
        "status",
        "created_at",
        "modified_at",
        "pdf_report_link",
        "report_request_payload",
        "report_response_data",)
    
    list_filter = ("phone_number","status", "created_at", "modified_at")
    search_fields = ("phone_number", "pan_number")
    readonly_fields = ("created_at", "modified_at")

    fieldsets = (
        ("Basic Info", {
            "fields": ("phone_number", "pan_number", "score", "status", "pdf_report_link")
        }),
        ("Trace Logs", {
            "fields": (
                "phone_to_pan_request",
                "phone_to_pan_response",
            )
        }),
        ("Timestamps", {
            "fields": ("created_at", "modified_at")
        }),
    )