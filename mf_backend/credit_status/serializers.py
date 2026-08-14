from rest_framework import serializers
from .models import CreditStatus
from account.serializers import BankAccountPostSerializer
from account.models import BankAccount
from utils.constants import ACCOUNT_PURPOSE

class CreditStatusGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditStatus
        fields="__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        context = self.context
        bank_accounts = BankAccount.objects.filter(account=instance.account, account_purpose__icontains=ACCOUNT_PURPOSE.E_NACH.value)
        if bank_accounts.exists():
            bank_serializer = BankAccountPostSerializer(bank_accounts, many=True, context=context)
            representation["bank_accounts"] = bank_serializer.data
        else:
            representation["bank_accounts"] = None

        return representation
    
class CreditStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditStatus
        fields="__all__"
