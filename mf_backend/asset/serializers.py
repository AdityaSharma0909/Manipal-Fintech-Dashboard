from rest_framework import serializers
from .models import Asset, GoldAppriaselModel, GoldPriceData, GoldPriceHistory
from document.serializers import AssetDocumentSerializer
from application.models import Application
from users.serializers import UserResponseSerializer
from django.utils import timezone
from datetime import timedelta as timedelta


import utils.helper as helper

class AssetSerializer(serializers.ModelSerializer):
    asset_documents = AssetDocumentSerializer(many=True,source="asset_document_asset",read_only=True)
    class Meta:
        model = Asset
        fields  = "__all__"

class GoldAppriaselSerializer(serializers.ModelSerializer):
    asset=AssetSerializer()
    appriased_by=UserResponseSerializer()
    class Meta:
        model = GoldAppriaselModel
        fields  = "__all__"

class GoldAppriaselCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoldAppriaselModel
        fields  = "__all__"
class AssetSerializerModified(serializers.ModelSerializer):
    asset_documents = AssetDocumentSerializer(many=True,source="asset_document_asset",read_only=True)
    # rate_per_gram=serializers.SerializerMethodField()
    processing_fee=serializers.SerializerMethodField()

    eligibility_amount_of_asset=serializers.SerializerMethodField()
    currentmarketvalue=serializers.SerializerMethodField()
    # net_weight_in_22_karats=serializers.SerializerMethodField()


    class Meta:
        model = Asset
        fields  = "__all__"
    # def get_rate_per_gram(self,obj):
    #     value=helper.rate_per_gram(obj.karat_value)
    #     return  round(value,2)
    def get_processing_fee(self,obj):

        return obj.asset_price* (obj.application.product.processing_fee)/100
    def get_eligibility_amount_of_asset(self,obj):
        price=float((obj.application.product.ltv_percentage))/100  * float(obj.asset_price)
        return round(price, 2)
    
    def get_currentmarketvalue(self,obj):
        # gold_price = helper.price_of_gold_22_karates()
        # price_of_22_karate = gold_price
        # price_of_22_karate = float(price_of_22_karate["gold_price__avg"])
        return helper.price_of_gold_22_karates()
    
    
    # def get_net_weight_in_22_karats(self,obj):
    #     weight=helper.customer_gold_weight_converter_to_22_karate_weight(obj.karat_value,obj.net_weight)
    #     return round(weight,2)


    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     asset_documents = AssetDocuments.objects.filter(asset=instance.asset_id)
    #     representation['asset_documents'] = AssetDocumentSerializer(asset_documents).data
    #     return representation

class AssetSingleSerializer(serializers.ModelSerializer):
    # asset_documents = AssetDocumentSerializer(many=True,source="asset_document_asset",read_only=True)
    eligible_amount=serializers.SerializerMethodField()
    leverage_amount=serializers.SerializerMethodField()
    class Meta:
        model = Asset
        fields  = "__all__"
    def get_eligible_amount(self,obj):
        price=Application.objects.get(application_id=obj.application_id).eligible_amount
        return  price
    def get_leverage_amount(self,obj):
        price=Application.objects.get(application_id=obj.application_id).eligible_amount
        amount=price*obj.leverage/100
        return  price +amount

class GoldPriceSerializer(serializers.ModelSerializer):
    karat = serializers.IntegerField()
    class Meta:
        model=GoldPriceData
        fields='__all__'
        extra_kwargs={'gold_price_id':{'read_only':True}}


class GoldPriceHistoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model=GoldPriceHistory
        fields='__all__'


class SimpleGoldPriceModelSerializer(serializers.ModelSerializer):
    historical_data = serializers.SerializerMethodField()

    class Meta:
        model=GoldPriceData
        fields='__all__'

    def get_historical_data(self, obj):
        date_week_behind = timezone.now() - timedelta(days=7)
        history_data = GoldPriceHistory.objects.filter(karat=obj.karat, lender=obj.lender,created_at__gte=date_week_behind)
        return GoldPriceHistoryModelSerializer(history_data, many=True).data


from lender.serializers import LenderSerializer
class GoldPriceModelSerializer(serializers.ModelSerializer):
    lender = LenderSerializer()
    class Meta:
        model=GoldPriceData
        fields='__all__'