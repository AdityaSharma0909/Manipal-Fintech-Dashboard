# models.py
from django.db import models
from users.models import User
from django.utils import timezone

class LeegalityDocument(models.Model):
    user = models.ForeignKey(
    User, on_delete=models.CASCADE,
    related_name="leegality_documents",
    null=True, blank=True
)

    agent_phone = models.CharField(max_length=20, null=True, blank=True)
    profile_id = models.CharField(max_length=100)
    document_id = models.CharField(max_length=100, null=True, blank=True)
    irn = models.CharField(max_length=100, null=True, blank=True)

    is_verified = models.BooleanField(default=False)

    audit_trail = models.TextField(null=True, blank=True)  # stores full base64 PDF content

    raw_response = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    STATUS_PENDING = "PENDING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    def __str__(self):
        return f"Document {self.document_id or 'Pending'}"


class Invitee(models.Model):
    document = models.ForeignKey(LeegalityDocument, related_name="invitees", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    sign_url = models.URLField(null=True, blank=True)
    active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name or "Invitee"