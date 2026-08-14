from apps.validators.base_validator import BaseValidator
from apps.common.exceptions.base_exception import ValidationException
from apps.common.constants.error_codes import ErrorCode


class LeadValidator(BaseValidator):
    """
    Validator for Customer CRM Lead data.
    """

    def validate(self, data: dict) -> None:
        """
        Generic validation entry point.
        """
        self.validate_lead_push(data)

    def validate_lead_push(self, data: dict) -> None:
        """
        Validates the data required to push a lead to ICICI CRM.
        Rules:
        - bank_id: > 0
        - first_name: 1-50 chars, no digits
        - last_name: 1-50 chars, no digits
        - mobile_number: starts with 6/7/8/9, 10 digits
        """
        self.require_fields(data, ["bank_id", "first_name", "last_name", "mobile_number", "user_id"])

        bank_id = data.get("bank_id")
        if not isinstance(bank_id, int) or bank_id <= 0:
            raise ValidationException(
                message="Bank ID must be greater than zero.",
                code=ErrorCode.VAL_INVALID_FIELD,
                errors={"bank_id": ["Invalid bank ID."]}
            )

        first_name = data.get("first_name")
        self.validate_name(first_name, "first_name")

        last_name = data.get("last_name")
        self.validate_name(last_name, "last_name")

        mobile_number = data.get("mobile_number")
        self.validate_mobile(mobile_number)

    def validate_name(self, name: str, field_name: str) -> None:
        """Helper to validate names (no digits, 1-50 chars)."""
        if not name or len(name) < 1 or len(name) > 50:
            raise ValidationException(
                message=f"{field_name.replace('_', ' ').capitalize()} must be between 1 and 50 characters.",
                code=ErrorCode.VAL_FIELD_TOO_LONG,
                errors={field_name: ["Invalid length."]}
            )
        
        if any(char.isdigit() for char in name):
            raise ValidationException(
                message=f"{field_name.replace('_', ' ').capitalize()} cannot contain numeric characters.",
                code=ErrorCode.VAL_INVALID_FORMAT,
                errors={field_name: ["Should not contain numbers."]}
            )
