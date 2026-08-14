from django.db import models


class CrifBureauTrace(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    reference_number = models.CharField(max_length=128, blank=True, null=True)
    pdf_report_link = models.CharField(max_length=512, blank=True, null=True)

    # Step 1: Phone-To-PAN data
    phone_to_pan_request = models.JSONField(default=dict, blank=True)
    phone_to_pan_response = models.JSONField(default=dict, blank=True)

    # Step 2: Consent creation data
    consent_request = models.JSONField(default=dict, blank=True)
    consent_response = models.JSONField(default=dict, blank=True)

    # Step 3: Webhook callback data
    webhook_payload = models.JSONField(default=dict, blank=True)
    decrypted_webhook_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} | {self.status} | Score: {self.score}"


class CrifBureauReportTrace(models.Model):
    class FileDownloadStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=FileDownloadStatus.choices,
        default=FileDownloadStatus.PENDING,
        db_index=True)
    
    pdf_report_link = models.CharField(max_length=512, blank=True, null=True)

    # Step 1: Phone-To-PAN data
    phone_to_pan_request = models.JSONField(default=dict, blank=True)
    phone_to_pan_response = models.JSONField(default=dict, blank=True)

    # Step 2: Crif report data
    report_request_payload = models.JSONField(default=dict, blank=True)
    report_response_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} | {self.status} | Score: {self.score}"
