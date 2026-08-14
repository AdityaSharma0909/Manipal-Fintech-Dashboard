import re
from django.conf import settings
from rest_framework import serializers


class CreateBajajFinServoLeadInitialRequestSerializer(serializers.Serializer):
    """

    Applies the custom validation constraints dynamically loaded from settings.
    """
    FullName = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={"required": "Please enter FullName", "blank": "Please enter FullName"}
    )
    MobileNo = serializers.CharField(
        required=True,
        error_messages={"required": "Please enter Mobile Number"}
    )
    LoanAmount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=True,
        error_messages={"required": "Please enter Loan Amount"}
    )
    
    Branch = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="Branch code, e.g. PUNE001",
        error_messages={
            "required": "Please enter Branch code",
            "blank": "Please enter Branch code"
        }
    )

    Type = serializers.CharField(
        required=True,
        allow_blank=False,
        help_text="Lead type for configuration selection, e.g. balance transfer or fresh lead",
        error_messages={
            "required": "Please enter Type",
            "blank": "Please enter Type"
        }
    )

    def validate_Type(self, value):
        normalized = value.strip().lower()
        supported_types = {key.strip().lower() for key in settings.BAJAJ_LEAD_TYPE_CONFIGS.keys()}
        if normalized not in supported_types:
            supported = ", ".join(sorted(settings.BAJAJ_LEAD_TYPE_CONFIGS.keys()))
            raise serializers.ValidationError(
                f"Unsupported Type. Supported types: {supported}"
            )
        return value.strip()

    def validate_FullName(self, value):
        min_len = settings.BAJAJ_VALIDATION.get('FULL_NAME_MIN_LENGTH', 1)
        max_len = settings.BAJAJ_VALIDATION.get('FULL_NAME_MAX_LENGTH', 80)

        if len(value.strip()) < min_len or len(value.strip()) > max_len:
            raise serializers.ValidationError(
                f"FullName must be between {min_len} and {max_len} characters"
            )
        return value.strip()

    def validate_MobileNo(self, value):
        # Match pattern: ^[0-9]{10}$
        if not re.match(r"^[0-9]{10}$", value):
            raise serializers.ValidationError("Mobile Number must be 10 digits")
        return value

    def validate_LoanAmount(self, value):
        min_amount = settings.BAJAJ_VALIDATION.get('LOAN_AMOUNT_MIN', 10000)
        max_amount = settings.BAJAJ_VALIDATION.get('LOAN_AMOUNT_MAX', 5000000)
        
        if value < min_amount or value > max_amount:
            raise serializers.ValidationError(
                f"Loan Amount must be between {int(min_amount)} and {int(max_amount)}"
            )
        return value


class BranchDetailSerializer(serializers.Serializer):
    BranchId = serializers.IntegerField()
    BranchName = serializers.CharField()
    BranchCode = serializers.CharField()


class BranchSummarySerializer(serializers.Serializer):
    branch_code = serializers.CharField()
    branch_name = serializers.CharField()


class BranchByPincodeRequestSerializer(serializers.Serializer):
    pincode = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={"required": "Pincode is required", "blank": "Pincode is required"}
    )

    def validate_pincode(self, value):
        if not re.match(r"^[0-9]{6}$", value):
            raise serializers.ValidationError("Invalid pincode")
        return value


class BranchByPincodeResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = BranchSummarySerializer(many=True)


class CreateLeadResultSerializer(serializers.Serializer):
    StatusCode = serializers.IntegerField()
    Status = serializers.CharField()
    LeadReference = serializers.CharField(allow_null=True)
    Message = serializers.CharField()
    Remarks = serializers.CharField()


class CommonResponseSerializer(serializers.Serializer):
    StatusCode = serializers.IntegerField()
    StatusMessage = serializers.CharField()
    Data = serializers.JSONField(allow_null=True)
