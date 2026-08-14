from rest_framework import serializers
from .models import Lender

import traceback


class LenderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Lender
        fields="__all__"


from asset.serializers import SimpleGoldPriceModelSerializer
class LenderGoldPriceSerializer(serializers.ModelSerializer):
    gold_prices = serializers.SerializerMethodField()
    
    class Meta:
        model = Lender
        fields="__all__"

    def get_gold_prices(self, obj):
        try:
            gold_prices = obj.lender_gold_price.filter(lender=obj.lender_id)
            return SimpleGoldPriceModelSerializer(gold_prices, many=True).data
        except Exception as e:
            traceback.print_exc()
            return []