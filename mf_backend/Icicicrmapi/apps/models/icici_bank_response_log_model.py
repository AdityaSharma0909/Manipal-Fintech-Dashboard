from django.db import models
from apps.models.base_model import BaseModel
from apps.models.icici_request_log_model import IciciRequestLog


class IciciBankResponseLog(BaseModel):
    """
    Model to store response payloads from ICICI CRM.
    """
    request_log = models.OneToOneField(
        IciciRequestLog, 
        on_delete=models.CASCADE, 
        related_name="response_log",
        help_text="Reference to the corresponding request log"
    )
    encrypted_response = models.TextField(help_text="Encrypted JSON response from ICICI")
    plain_response = models.TextField(help_text="Decrypted/Plain JSON response")
    lead_number = models.CharField(max_length=100, blank=True, null=True, help_text="Extracted lead number from response")
    lead_number_id = models.IntegerField(blank=True, null=True, help_text="Internal ID of the saved lead")
    status_code = models.CharField(max_length=10, blank=True, null=True)
    status_text = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "icici_bank_response_logs"
        verbose_name = "ICICI Bank Response Log"
        verbose_name_plural = "ICICI Bank Response Logs"

    def __str__(self):
        return f"Response Log for Request #{self.request_log_id}"
