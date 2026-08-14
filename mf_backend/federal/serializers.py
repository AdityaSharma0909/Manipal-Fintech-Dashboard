from rest_framework import serializers
from federal.models import SolidMapping, FederalBankApplication


class FederalBankApplicationModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = FederalBankApplication
        fields = "__all__"


class SolidMappingModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SolidMapping
        fields = "__all__"


class ListFederalBankApplicationModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = FederalBankApplication
        fields = [
            "federal_application_id",
            "is_existing_customer",
            "is_eligible",
            "agent_otp",
        ]
