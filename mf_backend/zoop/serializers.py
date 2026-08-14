from rest_framework import serializers
from .models import (
    PanVerification,BankVerification,DrivingLicenceVerification,
    ChequeOCRVerification,OCRLiteVerification,VoterIDAdvanceVerification,
    PassportAdvanceVerification,
    FaceMatchVerification
)


class PanVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanVerification
        fields = '__all__'


# Input request serializer
class PanVerificationRequestSerializer(serializers.Serializer):
    customer_pan_number = serializers.CharField(max_length=20)
    pan_holder_name = serializers.CharField(max_length=100)
    sub_task_tracker_id = serializers.UUIDField(required=False, allow_null=True)


class BankVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankVerification
        fields = '__all__'
        read_only_fields = [
            'request_id', 'group_id', 'success', 'response_code',
            'response_message', 'beneficiary_name', 'verification_status',
            'name_match_score', 'transaction_remark',
            'bank_name', 'branch', 'state', 'city', 'address'
        ]

class DrivingLicenceVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrivingLicenceVerification
        fields = '__all__'
        extra_kwargs = {
            'consent_text': {'required': False},
            'consent': {'required': False},
        }



class ChequeOCRVerificationSerializer(serializers.ModelSerializer):
    cheque_image = serializers.ImageField(required=True)  

    class Meta:
        model = ChequeOCRVerification
        fields = '__all__'
        extra_kwargs = {
            'consent_text': {'required': False},
            'consent': {'required': False},
        }


class OCRLiteVerificationSerializer(serializers.ModelSerializer):
    # These two fields will now accept image uploads directly
    card_front_image = serializers.ImageField(required=True)
    card_back_image = serializers.ImageField(required=False)
    sub_task_tracker_id = serializers.UUIDField(required=False, allow_null=True)

    # Default consent values (no need for user to manually send)
    consent = serializers.CharField(default="Y")
    consent_text = serializers.CharField(
        default="I hereby declare my consent agreement for fetching my information via ZOOP API"
    )

    class Meta:
        model = OCRLiteVerification
        fields = '__all__'


    
class VoterIDAdvanceVerificationSerializer(serializers.ModelSerializer):

    # Zoop Response Fields -> READ ONLY
    request_id = serializers.CharField(read_only=True)
    group_id = serializers.CharField(read_only=True)
    success = serializers.BooleanField(read_only=True)
    response_code = serializers.CharField(read_only=True)
    response_message = serializers.CharField(read_only=True)
    name_match_score = serializers.CharField(read_only=True)
    voter_last_updated_date = serializers.CharField(read_only=True)

    user_name_english = serializers.CharField(read_only=True)
    user_name_vernacular = serializers.CharField(read_only=True)
    user_gender = serializers.CharField(read_only=True)
    user_age = serializers.IntegerField(read_only=True)

    relative_name_english = serializers.CharField(read_only=True)
    relative_name_vernacular = serializers.CharField(read_only=True)
    relative_relation = serializers.CharField(read_only=True)

    assembly_constituency_name = serializers.CharField(read_only=True)
    constituency_part_number = serializers.IntegerField(read_only=True)
    serial_number_applicable_part = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = VoterIDAdvanceVerification
        fields = "__all__"


class PassportAdvanceVerificationSerializer(serializers.ModelSerializer):

    def validate_customer_file_number(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("customer_file_number must be at least 12 characters long.")
        return value

    def validate_customer_dob(self, value):
        # Ensure dd-mm-yyyy format
        import re
        if not re.match(r"^\d{2}-\d{2}-\d{4}$", value):
            raise serializers.ValidationError("DOB must be in format DD-MM-YYYY")
        return value

    class Meta:
        model = PassportAdvanceVerification
        fields = '__all__'
        read_only_fields = [
            "request_id", "group_id", "success", "response_code",
            "response_message", "passport_status", "name_on_passport",
            "customer_last_name", "passport_number", "passport_applied_date",
            "name_match_score", "customer_dob_result"
        ]


class FaceMatchVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceMatchVerification
        fields = '__all__'


class FaceMatchRequestSerializer(serializers.Serializer):
    card_image = serializers.CharField(required=True, help_text="Base64 encoded string of card image")
    user_image = serializers.CharField(required=True, help_text="Base64 encoded string of user image")
    consent = serializers.CharField(default="Y")
    consent_text = serializers.CharField(
        default="I hereby declare my consent agreement for fetching my information via ZOOP API"
    )
    sub_task_tracker_id = serializers.UUIDField(required=False, allow_null=True)


