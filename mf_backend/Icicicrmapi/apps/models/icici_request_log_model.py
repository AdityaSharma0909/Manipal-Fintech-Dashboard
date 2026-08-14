from django.db import models
from apps.models.base_model import BaseModel


class IciciRequestLog(BaseModel):
    """
    Model to store incoming request payloads to ICICI CRM.
    """
    mobile_number = models.CharField(max_length=20)
    plain_request = models.TextField(help_text="Decrypted/Plain JSON request payload")
    encrypted_request = models.TextField(help_text="Encrypted payload sent to ICICI")
    correlation_id = models.CharField(max_length=200, blank=True, null=True, help_text="X-Correlation-ID for tracking")

    class Meta:
        db_table = "icici_request_logs"
        verbose_name = "ICICI Request Log"
        verbose_name_plural = "ICICI Request Logs"
        indexes = [
            models.Index(fields=["mobile_number"], name="idx_req_log_mobile"),
            models.Index(fields=["correlation_id"], name="idx_req_log_corr_id"),
        ]

    def __str__(self):
        return f"Request Log #{self.id} ({self.mobile_number})"
