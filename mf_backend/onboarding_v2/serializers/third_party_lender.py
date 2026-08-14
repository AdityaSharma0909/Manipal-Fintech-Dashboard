from rest_framework import serializers
from onboarding_v2.models import ThirdPartyLender

class ThirdPartyLenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThirdPartyLender
        fields = ['id', 'bank_name', 'ifsc_code', 'branch']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ThirdPartyLender.objects.all(),
                fields=['bank_name', 'ifsc_code'],
                message="A lender with this bank name and IFSC code already exists."
            )
        ]
