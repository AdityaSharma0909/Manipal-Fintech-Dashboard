from django.db import models
from apps.models.base_model import BaseModel


class IciciAppSetting(BaseModel):
    """
    Model to store ICICI Bank specific application settings for CRM integration.
    """
    bank_id = models.IntegerField(unique=True, help_text="Unique identifier for the bank (default: 1 for ICICI)")
    token_url = models.CharField(max_length=500, help_text="Endpoint URL to fetch access token")
    client_id = models.CharField(max_length=200, help_text="API Client ID provided by ICICI")
    client_secret = models.CharField(max_length=500, help_text="API Client Secret provided by ICICI")
    customer_url = models.CharField(max_length=500, help_text="Endpoint URL for pushing lead details")
    is_async = models.BooleanField(default=False, help_text="Whether to process the request asynchronously")
    call_back_url = models.CharField(max_length=500, blank=True, default="", help_text="Callback URL for async response")
    country_code = models.CharField(max_length=10, blank=True, default="IN")
    lead_source = models.CharField(max_length=100, blank=True, default="")
    product = models.CharField(max_length=100, blank=True, default="")
    lead_channel = models.CharField(max_length=100, blank=True, default="")
    partner_id = models.CharField(max_length=100, blank=True, default="")
    sub_agent_code = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "icici_app_settings"
        verbose_name = "ICICI App Setting"
        verbose_name_plural = "ICICI App Settings"
        indexes = [
            models.Index(fields=["bank_id"], name="idx_icici_settings_bank_id"),
        ]

    def __str__(self):
        return f"ICICI Settings (BankId={self.bank_id})"
