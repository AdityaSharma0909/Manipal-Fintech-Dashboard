"""
apps/business/services/base_service.py
=======================================
Base Service (Business Layer).

All business logic services must inherit from BaseService.

Responsibilities:
  - Orchestrate business logic and workflows
  - Call repositories (data layer) — never ORM directly
  - Call integrations (external APIs) via utility clients
  - Raise domain-level exceptions (NOT HTTP exceptions)
  - Must NOT contain raw SQL, ORM queries, or HTTP request code

Usage:
    from apps.business.services.base_service import BaseService
    from apps.data.repositories.customer_repository import CustomerRepository

    class CustomerService(BaseService):
        def __init__(self):
            self.repository = CustomerRepository()

        def get_customer(self, customer_id: str):
            customer = self.repository.get_by_id(customer_id)
            if customer is None:
                raise ResourceNotFoundException(f"Customer {customer_id} not found.")
            return customer
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseService:
    """
    Abstract base class for all business service classes.

    Provides:
      - Standardized logger scoped to the concrete service class name
      - Placeholder hooks for pre/post execution logic (override as needed)
    """

    def __init__(self):
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    def _log_operation(self, operation: str, context: Any = None) -> None:
        """
        Log a business operation for audit/debug purposes.

        Args:
            operation: Human-readable description of the operation.
            context: Optional context data (dict, str, etc.) to include in log.
        """
        self.logger.info(
            "Service operation: %s | context: %s",
            operation,
            context,
        )

    def _log_error(self, operation: str, error: Exception) -> None:
        """
        Log an error during a business operation.

        Args:
            operation: Human-readable description of the operation.
            error: The caught exception.
        """
        self.logger.error(
            "Service error in %s | error: %s",
            operation,
            str(error),
            exc_info=True,
        )
