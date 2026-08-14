from rest_framework import serializers

from onboarding_v2.models import PincodeMaster


class PincodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PincodeMaster
        fields = "__all__"
