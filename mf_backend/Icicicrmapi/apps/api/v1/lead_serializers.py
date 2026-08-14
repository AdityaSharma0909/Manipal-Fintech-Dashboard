"""
apps/api/v1/lead_serializers.py
================================
DRF serializers for the ICICI CRM Lead push endpoint.

Validation rules (parity with FluentValidation on C# CustomerCrmDetails):
  - userId      : optional string, max 100 chars
  - bankId      : required integer > 0
  - firstName   : required, 1–50 chars, no digit characters
  - lastName    : required, 1–50 chars, no digit characters
  - mobileNumber: required, regex ^[6789]\d{9}$ (Indian 10-digit mobile)
"""

import re

from rest_framework import serializers

from apps.models.lead_model import CustomerCrmLead


# ---------------------------------------------------------------------------
# Request Serializer
# ---------------------------------------------------------------------------

class LeadPushRequestSerializer(serializers.Serializer):
    """
    Deserializes and validates the POST /api/v1/icici-crm/push-lead/ body.

    Mirrors the C# ``CustomerCrmDetails`` model with camelCase field names
    so the JSON payload is accepted as-is from the client.
    ``source=`` maps each camelCase key to its snake_case counterpart in
    ``validated_data``, which the service layer consumes directly.
    """

    # ------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------

    userId = serializers.CharField(
        source="user_id",
        required=False,          # Optional in C# model (no validation rule)
        allow_blank=True,
        allow_null=True,
        max_length=100,
        help_text="Optional caller-assigned user identifier.",
    )

    bankId = serializers.IntegerField(
        source="bank_id",
        required=True,
        min_value=1,             # BankId > 0
        help_text="Bank identifier. Must be a positive integer (> 0).",
    )

    firstName = serializers.CharField(
        source="first_name",
        required=True,
        min_length=1,
        max_length=50,
        help_text="Customer first name. 1–50 characters, no digits allowed.",
    )

    lastName = serializers.CharField(
        source="last_name",
        required=True,
        min_length=1,
        max_length=50,
        help_text="Customer last name. 1–50 characters, no digits allowed.",
    )

    mobileNumber = serializers.CharField(
        source="mobile_number",
        required=True,
        help_text="10-digit Indian mobile number starting with 6, 7, 8, or 9.",
    )

    # ------------------------------------------------------------------
    # Field-level validators
    # ------------------------------------------------------------------

    def validate_firstName(self, value: str) -> str:  # noqa: N802
        """First name must not contain any numeric characters."""
        if re.search(r"\d", value):
            raise serializers.ValidationError(
                "First name must not contain numbers."
            )
        return value.strip()

    def validate_lastName(self, value: str) -> str:  # noqa: N802
        """Last name must not contain any numeric characters."""
        if re.search(r"\d", value):
            raise serializers.ValidationError(
                "Last name must not contain numbers."
            )
        return value.strip()

    def validate_mobileNumber(self, value: str) -> str:  # noqa: N802
        """Indian mobile number: exactly 10 digits, starting with 6/7/8/9."""
        pattern = re.compile(r"^[6789]\d{9}$")
        if not pattern.match(value.strip()):
            raise serializers.ValidationError(
                "Invalid mobile number. "
                "Must be exactly 10 digits and start with 6, 7, 8, or 9."
            )
        return value.strip()


# ---------------------------------------------------------------------------
# Response Serializers
# ---------------------------------------------------------------------------

class LeadPushSuccessResponseSerializer(serializers.Serializer):
    """
    Shape of the success response body for the push-lead endpoint.
    Used only for Swagger schema generation.
    """

    success = serializers.BooleanField(
        default=True,
        help_text="Always ``true`` on a successful lead push.",
    )
    message = serializers.CharField(
        default="Lead pushed successfully.",
        help_text="Human-readable status message.",
    )


class LeadResponseSerializer(serializers.ModelSerializer):
    """
    Full lead record serializer (used internally / admin endpoints).
    """

    class Meta:
        model = CustomerCrmLead
        fields = [
            "id",
            "first_name",
            "last_name",
            "mobile_number",
            "icici_lead_number",
            "created_at",
        ]
        read_only_fields = fields
