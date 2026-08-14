from attr import attrs
from rest_framework import serializers


class PhoneToPanSerializer(serializers.Serializer):

    phoneNumber = serializers.CharField(
        required=False,
        allow_blank=True)

    firstName = serializers.CharField(
        required=False,
        allow_blank=True)

    lastName = serializers.CharField(
        required=False,
        allow_blank=True)

    address = serializers.CharField(
        required=False,
        allow_blank=True)

    pincode = serializers.CharField(
        required=False,
        allow_blank=True)

    panNumber = serializers.CharField(
        required=False,
        allow_blank=True)

    def validate(self, attrs):
        pan_number = (attrs.get("panNumber", "").strip())

        if pan_number:
           return attrs

        errors = {}

        phone_number = (attrs.get("phoneNumber", "").strip())

        if not phone_number:
           errors["phoneNumber"] = ("Phone number is missing.")

        elif not phone_number.isdigit():
            errors["phoneNumber"] = (
            "Phone number must contain only digits.")

        elif len(phone_number) != 10:
            errors["phoneNumber"] = ("Phone number must be exactly 10 digits.")

        if errors:
            raise serializers.ValidationError(errors)

        required_fields = {
        "firstName": "First name is missing.",
        "lastName": "Last name is missing.",
        "address": "Address is missing.",
        "pincode": "PinCode is missing."}

        for field, message in required_fields.items():
            value = (
            attrs.get(field, "")
            .strip())

            if not value:
               errors[field] = message

        pincode = (attrs.get("pincode", "").strip())

        if pincode:
            if not pincode.isdigit() or len(pincode) != 6:
                errors["pincode"] = ("PinCode must be exactly 6 digits.")

        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class SendCrifRequestSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(max_length=15)
    firstName = serializers.CharField(max_length=100)
    lastName = serializers.CharField(max_length=100)
    dateOfBirth = serializers.DateField(
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
        required=False,
        allow_null=True,
    )
    panNumber = serializers.CharField(max_length=20, required=False, allow_blank=True)
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255)
    pincode = serializers.CharField(max_length=10)
    callbackUrl = serializers.URLField()
    productName = serializers.ListField(child=serializers.CharField(), allow_empty=False)
    otpBypass = serializers.CharField(max_length=10)


class RequestDataSerializer(serializers.Serializer):
    requestData = serializers.CharField()


class CrifWebhookSerializer(serializers.Serializer):
    requestData = serializers.CharField(required=False, allow_blank=True)

class ConsentSerializer(serializers.Serializer):
    consentFlag = serializers.BooleanField(default=False)
    consentTimestamp = serializers.IntegerField(min_value=1)
    consentIpAddress = serializers.IPAddressField()
    consentMessageId = serializers.CharField(max_length=100)

class CrifReportSerializer(serializers.Serializer):

    phoneNumber = serializers.CharField(max_length=15)
    firstName = serializers.CharField(max_length=100)
    lastName = serializers.CharField(max_length=100)
    dateOfBirth = serializers.DateField(
            format="%Y-%m-%d",
            input_formats=["%Y-%m-%d"],
            required=False,
            allow_null=True,)
    pan = serializers.CharField(max_length=20, required=False, allow_blank=True)
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True)
    address = serializers.CharField(max_length=255)
    pincode = serializers.CharField(max_length=10) 
    consent = ConsentSerializer()
    