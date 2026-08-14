
from rest_framework  import serializers
from payment.models import Repayment , BharatSwasthyaRepayment, SalesOfficerPayout
from loan.models import Loan
from loan.serializer import LoanSerializer
from application.serializers import ApplicationModelSerializer

class RepaymentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["loan"] = LoanSerializer(instance.loan).data
        return representation


class RepaymentStatusSerializer(serializers.ModelSerializer):
    loan=LoanSerializer()
    class Meta:
        model = Repayment
        fields = "__all__"

class BharatSwasthyaRepaymentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BharatSwasthyaRepayment
        fields = "__all__"

class SalesOfficerPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOfficerPayout
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        app = getattr(instance, "application", None)
        if app:
            data["application"] = ApplicationModelSerializer(app).data
        return data
