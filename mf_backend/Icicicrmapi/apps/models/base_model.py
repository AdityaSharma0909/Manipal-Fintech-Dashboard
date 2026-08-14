"""
apps/models/base_model.py
=========================
Base abstract Django model.
All project models must inherit from BaseModel to ensure:
  - UUID primary key (avoids sequential integer exposure)
  - Automatic created_at / updated_at timestamps
  - Soft-delete support via is_active flag
  - Uniform __str__ representation

Usage:
    from apps.models.base_model import BaseModel

    class Customer(BaseModel):
        name = models.CharField(max_length=255)
"""

import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model providing common fields for all entities.

    Fields:
        id          (UUIDField)      — Auto-generated UUID primary key.
        created_at  (DateTimeField)  — Auto-set on record creation.
        updated_at  (DateTimeField)  — Auto-updated on every save.
        is_active   (BooleanField)   — Soft-delete flag; False = logically deleted.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"

    def soft_delete(self) -> None:
        """Mark record as inactive (logical delete). Does NOT remove from DB."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])
