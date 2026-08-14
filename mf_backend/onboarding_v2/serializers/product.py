from rest_framework import serializers

from onboarding_v2.models import ProductV2


class ProductV2Serializer(serializers.ModelSerializer):
    class Meta:
        model = ProductV2
        fields = (
            "id",
            "available_for",
            "category",
            "product_code",
            "repayment_frequency",
            "tenure_months",
            "ltv",
            "minimum_ticket_size",
            "maximum_ticket_size",
            "interest_rate",
            "processing_fees",
            "processing_fees_with_cbo_approval",
            "monthly_penalty_on_principal_outstanding",
            "non_release_penalty",
            "foreclosure_charges",
            "stamp_duty",
            "metadata",
        )
