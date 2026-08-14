"""
apps/data/repositories/base_repository.py
==========================================
Base Repository (Data Access Layer).

Provides a generic CRUD abstraction over Django ORM.
All concrete repositories must inherit from BaseRepository[Model].

Responsibilities:
  - Execute all database queries (SELECT, INSERT, UPDATE, DELETE)
  - Keep all ORM logic here — NO ORM calls in services or views
  - Return model instances or QuerySets; never raw SQL unless necessary
  - Apply soft-delete filtering by default (is_active=True)

Usage:
    from apps.data.repositories.base_repository import BaseRepository
    from apps.models.customer import Customer

    class CustomerRepository(BaseRepository[Customer]):
        model = Customer

        def find_by_email(self, email: str):
            return self.get_queryset().filter(email=email).first()
"""

import logging
from typing import Generic, TypeVar, Optional, List, Type
from django.db import models as django_models

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=django_models.Model)


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository providing standard CRUD operations.

    Attributes:
        model (Type[ModelType]): The Django model class this repository manages.
    """

    model: Type[ModelType]

    # -------------------------------------------------------------------------
    # Query helpers
    # -------------------------------------------------------------------------

    def get_queryset(self) -> django_models.QuerySet:
        """Return the default active QuerySet (soft-delete aware)."""
        qs = self.model.objects.all()
        # Apply is_active filter if the model has the field (from BaseModel)
        if hasattr(self.model, "is_active"):
            qs = qs.filter(is_active=True)
        return qs

    def get_all_queryset(self) -> django_models.QuerySet:
        """Return QuerySet including soft-deleted records."""
        return self.model.objects.all()

    # -------------------------------------------------------------------------
    # Read operations
    # -------------------------------------------------------------------------

    def get_by_id(self, record_id) -> Optional[ModelType]:
        """Fetch a single active record by primary key. Returns None if not found."""
        try:
            return self.get_queryset().get(pk=record_id)
        except self.model.DoesNotExist:
            logger.debug("%s with id=%s not found.", self.model.__name__, record_id)
            return None

    def get_all(self) -> django_models.QuerySet:
        """Return all active records."""
        return self.get_queryset()

    def filter(self, **kwargs) -> django_models.QuerySet:
        """Filter active records by arbitrary kwargs."""
        return self.get_queryset().filter(**kwargs)

    def exists(self, **kwargs) -> bool:
        """Check if any active record matching kwargs exists."""
        return self.get_queryset().filter(**kwargs).exists()

    def count(self, **kwargs) -> int:
        """Count active records matching optional kwargs."""
        return self.get_queryset().filter(**kwargs).count()

    # -------------------------------------------------------------------------
    # Write operations
    # -------------------------------------------------------------------------

    def create(self, **kwargs) -> ModelType:
        """Create and persist a new record."""
        instance = self.model(**kwargs)
        instance.save()
        logger.debug("Created %s: id=%s", self.model.__name__, instance.pk)
        return instance

    def update(self, instance: ModelType, **kwargs) -> ModelType:
        """Update fields on an existing instance and save."""
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.save(update_fields=list(kwargs.keys()) + ["updated_at"])
        logger.debug("Updated %s: id=%s", self.model.__name__, instance.pk)
        return instance

    def delete(self, instance: ModelType) -> None:
        """Soft-delete a record (sets is_active=False). Does NOT hard-delete."""
        if hasattr(instance, "soft_delete"):
            instance.soft_delete()
            logger.debug("Soft-deleted %s: id=%s", self.model.__name__, instance.pk)
        else:
            instance.delete()
            logger.debug("Hard-deleted %s: id=%s", self.model.__name__, instance.pk)

    def hard_delete(self, instance: ModelType) -> None:
        """Permanently remove a record from the database. Use with caution."""
        pk = instance.pk
        instance.delete()
        logger.warning("Hard-deleted %s: id=%s", self.model.__name__, pk)

    def bulk_create(self, instances: List[ModelType]) -> List[ModelType]:
        """Bulk insert multiple instances. Returns created instances."""
        created = self.model.objects.bulk_create(instances)
        logger.debug("Bulk created %d %s records.", len(created), self.model.__name__)
        return created
