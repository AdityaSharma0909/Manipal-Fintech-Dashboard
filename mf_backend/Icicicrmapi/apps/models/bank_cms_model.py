from django.db import models
from apps.models.base_model import BaseModel


class BankCms(BaseModel):
    """
    Model for managing dynamic content (CMS) for bank-related communications or UI.
    """
    bank_id = models.IntegerField(help_text="Identifier for the bank")
    slug = models.SlugField(max_length=100, unique=True, help_text="Unique identifier for the CMS content block")
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="The actual CMS content (HTML or plain text)")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional configuration for this content")
    is_published = models.BooleanField(default=True)

    class Meta:
        db_table = "bank_cms"
        verbose_name = "Bank CMS"
        verbose_name_plural = "Bank CMS Blocks"
        indexes = [
            models.Index(fields=["bank_id", "slug"], name="idx_bank_cms_lookup"),
        ]

    def __str__(self):
        return f"{self.title} ({self.slug})"
