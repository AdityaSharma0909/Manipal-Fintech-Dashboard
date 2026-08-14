from django.db import models
from apps.models.base_model import BaseModel


class NotificationMaster(BaseModel):
    """
    Master model for notification templates (SMS, Email, etc.)
    """
    TYPE_CHOICES = [
        ("SMS", "Short Message Service"),
        ("EMAIL", "Email Notification"),
        ("PUSH", "Push Notification"),
    ]

    template_code = models.CharField(max_length=50, unique=True, help_text="Unique code for the template (e.g., LEAD_SUCCESS)")
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=255, blank=True, null=True)
    body_template = models.TextField(help_text="Template content with placeholders (e.g., Hello {{name}})")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_master"
        verbose_name = "Notification Master"
        verbose_name_plural = "Notification Master Templates"

    def __str__(self):
        return f"{self.name} [{self.template_code}]"
