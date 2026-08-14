from rest_framework import serializers

from onboarding_v2.constants import LeadType
from onboarding_v2.models import BankBranch, LendingPartnerMaster, CustomerBankAccount


class BankBranchSerializer(serializers.ModelSerializer):
    """Full serializer — used for detail GET and PATCH."""

    class Meta:
        model = BankBranch
        fields = "__all__"


class BankBranchListSerializer(serializers.ModelSerializer):
    """Slim serializer for the paginated list view — only list-display columns."""

    class Meta:
        model = BankBranch
        fields = [
            "id",
            "bank_name",
            "branch_name",
            "ifsc_code",
            "branch_code",
            "sol_id",
            "district",
            "state",
            "pincode",
            "created_at",
        ]


class BankBranchCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a single bank branch record.

    Mandatory: bank_name, branch_name, state, district, pincode.
    Non-mandatory: ifsc_code, branch_code, address, city, sol_id.
    """

    bank_name = serializers.CharField(
        max_length=255,
        error_messages={"required": "Bank name is required.", "blank": "Bank name cannot be blank."},
    )
    branch_name = serializers.CharField(
        max_length=255,
        error_messages={"required": "Branch name is required.", "blank": "Branch name cannot be blank."},
    )
    state = serializers.CharField(
        max_length=255,
        error_messages={"required": "State is required.", "blank": "State cannot be blank."},
    )
    district = serializers.CharField(
        max_length=255,
        error_messages={"required": "District is required.", "blank": "District cannot be blank."},
    )
    pincode = serializers.CharField(
        max_length=10,
        error_messages={"required": "Pincode is required.", "blank": "Pincode cannot be blank."},
    )
    # Optional fields
    ifsc_code = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True, default=None)
    branch_code = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True, default=None)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)
    city = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True, default=None)
    sol_id = serializers.CharField(max_length=64, required=False, allow_blank=True, allow_null=True, default=None)

    class Meta:
        model = BankBranch
        fields = [
            "bank_name",
            "branch_name",
            "ifsc_code",
            "branch_code",
            "address",
            "city",
            "state",
            "district",
            "sol_id",
            "pincode",
        ]


class LendingPartnerMasterSerializer(serializers.ModelSerializer):
    available_for_lead_type = serializers.ListField(
        child=serializers.ChoiceField(
            choices=(
                LeadType.CO_LENDING,
                LeadType.FRESH,
                LeadType.BALANCE_TRANSFER,
                LeadType.SELF_LENDING,
            )
        ),
        required=False,
        allow_empty=True,
    )

    def validate_available_for_lead_type(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate lead types are not allowed.")
        return value

    class Meta:
        model = LendingPartnerMaster
        fields = "__all__"


class CustomerBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerBankAccount
        fields = "__all__"
