from rest_framework import serializers

from loan.models import LoanPaymentTransaction


class LoanPaymentTransactionSerializer(serializers.ModelSerializer):

    payment_date=serializers.DateField(input_formats=['%d-%m-%Y', '%d/%m/%Y','%Y-%m-%d','%Y/%m/%d'])
    class Meta:
        model=LoanPaymentTransaction
        fields='__all__'