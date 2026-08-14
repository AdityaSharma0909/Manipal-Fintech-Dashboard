from rest_framework import serializers


class CoverFoxSerializer(serializers.Serializer):
    name = serializers.CharField(
        required=True,
        error_messages={
            "required": "Name is missing.",
            "blank": "Name is missing.",
        },
    )
    mobile = serializers.CharField(
        required=True,
        error_messages={
            "required": "Mobile is missing.",
            "blank": "Mobile is missing.",
        },
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "Email is missing.",
            "blank": "Email is missing.",
        },
    )

    def validate_mobile(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
        return value


class MediBuddySerializer(serializers.Serializer):
    mobileNumber = serializers.CharField(
        required=True,
        error_messages={
            "required": "Mobile is missing.",
            "blank": "Mobile is missing.",
        },
    )
    employeeId=serializers.CharField(required=True)
    def validate_mobileNumber(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Mobile number must be exactly 10 digits.")
        return value
