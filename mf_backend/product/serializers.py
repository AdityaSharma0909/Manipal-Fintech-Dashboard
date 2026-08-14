from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import Product
from lender.serializers import LenderSerializer
from lender.models import Lender
from .models import WhiteGoods, ProductSpecificDocuments, ProductWhiteGoodsMapping


class WhiteGoodsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhiteGoods
        fields = [
            "goods_id",
            "goods_name",
            "goods_description",
            "goods_price",
        ]


class WhiteGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhiteGoods
        fields = "__all__"


class WhiteGoodsQuantitySerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(required=False)

    class Meta:
        model = WhiteGoods
        fields = "__all__"


class ProductSpecificDocumentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductSpecificDocuments
        fields = "__all__"


class ProductSpecificDocumentsSerializerSmall(serializers.ModelSerializer):

    class Meta:
        model = ProductSpecificDocuments
        fields = ["document_name", "document_type"]


class ProductSerializer(serializers.ModelSerializer):

    goods = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    lender = LenderSerializer()

    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            contra_loan_details = (
                Product.objects.values()
                .filter(product_id=representation["contra_product"])
                .first()
            )
        except Exception as e:
            contra_loan_details = []
        representation["contra_product"] = contra_loan_details
        return representation

    def get_goods(self, obj):
        goods = ProductWhiteGoodsMapping.objects.filter(product=obj.product_id)
        li = []
        for good in goods:

            li.append(WhiteGoodsSerializer(good.goods).data)

        return li

    def get_documents(self, obj):
        good = ProductSpecificDocuments.objects.filter(product=obj.product_id)
        serializer = ProductSpecificDocumentsSerializer(good, many=True)
        return serializer.data


class SingleProductSerializer(serializers.ModelSerializer):
    lender = LenderSerializer()

    class Meta:
        model = Product
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            contra_loan_details = (
                Product.objects.values()
                .filter(product_id=representation["contra_product"])
                .first()
            )
        except Exception as e:
            contra_loan_details = []
        representation["contra_product"] = contra_loan_details
        return representation


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductWhiteGoodsMappingSerializer(serializers.ModelSerializer):

    goods = WhiteGoodsSerializer()

    class Meta:
        model = ProductWhiteGoodsMapping
        fields = "__all__"
