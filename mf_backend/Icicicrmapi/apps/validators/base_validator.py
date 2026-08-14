"""
apps/validators/base_validator.py
=====================================
Base validator classes for the validation layer.

Design:
  - Validators live in the validators/ layer, NOT in serializers or views.
  - Serializers handle deserialization + field-level validation.
  - Validators handle cross-field, business-rule, and domain-level validation.
  - Services call validators before executing business logic.

Hierarchy:
  BaseValidator
    └── FieldValidator      ← single field validation helpers
    └── RequestValidator    ← full request object validation (cross-field)
    └── BusinessRuleValidator ← domain-specific rule checks

Usage:
    class LeadValidator(BaseValidator):
        def validate(self, data: dict) -> None:
            self.require_fields(data, ["mobile", "product_code"])
            self.validate_mobile(data["mobile"])
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Any

from apps.common.exceptions.base_exception import ValidationException
from apps.common.constants.error_codes import ErrorCode

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """
    Abstract base for all domain validators.

    Subclasses must implement validate(data).
    All validation errors must raise ValidationException with structured details.

    Usage:
        validator = MyValidator()
        validator.validate(data)   # raises ValidationException on failure
    """

    @abstractmethod
    def validate(self, data: Any) -> None:
        """
        Validate the given data.

        Args:
            data: The data to validate (dict, DTO, or primitive).

        Raises:
            ValidationException: If validation fails.
        """
        raise NotImplementedError

    # -------------------------------------------------------------------------
    # Protected helper methods available to all validators
    # -------------------------------------------------------------------------

    def require_fields(self, data: dict, fields: list[str]) -> None:
        """
        Assert that all listed keys are present and non-empty in data.

        Args:
            data:   The dict to check.
            fields: List of required key names.

        Raises:
            ValidationException: If any required field is missing or empty.
        """
        missing = [f for f in fields if not data.get(f)]
        if missing:
            raise ValidationException(
                message=f"Required fields missing or empty: {', '.join(missing)}",
                code=ErrorCode.VAL_MISSING_REQUIRED_FIELD,
                errors={field: ["This field is required."] for field in missing},
            )

    def validate_mobile(self, mobile: str, field_name: str = "mobile") -> None:
        """
        Validate Indian mobile number (10 digits, starts with 6-9).

        Args:
            mobile:     The mobile number string to validate.
            field_name: Field name for error reporting.

        Raises:
            ValidationException: If format is invalid.
        """
        pattern = r"^[6-9]\d{9}$"
        if not re.match(pattern, str(mobile).strip()):
            raise ValidationException(
                message=f"Invalid mobile number: '{mobile}'. Must be 10 digits starting with 6-9.",
                code=ErrorCode.VAL_INVALID_MOBILE,
                errors={field_name: ["Invalid Indian mobile number format."]},
            )

    def validate_email(self, email: str, field_name: str = "email") -> None:
        """
        Basic email format validation.

        Raises:
            ValidationException: If format is invalid.
        """
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, str(email).strip()):
            raise ValidationException(
                message=f"Invalid email address: '{email}'.",
                code=ErrorCode.VAL_INVALID_EMAIL,
                errors={field_name: ["Invalid email address format."]},
            )

    def validate_pan(self, pan: str, field_name: str = "pan") -> None:
        """
        Validate Indian PAN card number format (e.g., ABCDE1234F).

        Raises:
            ValidationException: If format is invalid.
        """
        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
        if not re.match(pattern, str(pan).strip().upper()):
            raise ValidationException(
                message=f"Invalid PAN number: '{pan}'.",
                code=ErrorCode.VAL_INVALID_PAN,
                errors={field_name: ["PAN must be in format: ABCDE1234F."]},
            )

    def validate_min_length(
        self, value: str, min_length: int, field_name: str
    ) -> None:
        """
        Validate minimum string length.

        Raises:
            ValidationException: If value is shorter than min_length.
        """
        if len(str(value)) < min_length:
            raise ValidationException(
                message=f"'{field_name}' must be at least {min_length} characters.",
                code=ErrorCode.VAL_FIELD_TOO_SHORT,
                errors={field_name: [f"Minimum length is {min_length} characters."]},
            )

    def validate_max_length(
        self, value: str, max_length: int, field_name: str
    ) -> None:
        """
        Validate maximum string length.

        Raises:
            ValidationException: If value exceeds max_length.
        """
        if len(str(value)) > max_length:
            raise ValidationException(
                message=f"'{field_name}' must not exceed {max_length} characters.",
                code=ErrorCode.VAL_FIELD_TOO_LONG,
                errors={field_name: [f"Maximum length is {max_length} characters."]},
            )

    def validate_positive_integer(self, value: Any, field_name: str) -> None:
        """
        Validate that value is a positive integer (> 0).

        Raises:
            ValidationException: If value is not a positive integer.
        """
        try:
            int_val = int(value)
            if int_val <= 0:
                raise ValueError
        except (TypeError, ValueError):
            raise ValidationException(
                message=f"'{field_name}' must be a positive integer.",
                code=ErrorCode.VAL_INVALID_VALUE,
                errors={field_name: ["Must be a positive integer greater than 0."]},
            )

    def validate_allowed_values(
        self, value: Any, allowed: list, field_name: str
    ) -> None:
        """
        Validate that value is within an allowed set.

        Raises:
            ValidationException: If value is not in the allowed set.
        """
        if value not in allowed:
            raise ValidationException(
                message=f"'{field_name}' has an invalid value: '{value}'. "
                        f"Allowed: {allowed}",
                code=ErrorCode.VAL_INVALID_VALUE,
                errors={field_name: [f"Must be one of: {', '.join(str(a) for a in allowed)}."]},
            )
