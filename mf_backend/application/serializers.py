from django.db.models import Sum
from rest_framework import serializers
from decimal import Decimal
from disbursements.serializers import DisbursementSerializer
from lender.models import Lender
from loan.models import Loan

from .models import Application, ApplicationGoodsMapping , ApplicationDocument, NewApplication
from product.models import WhiteGoods, Product
from product.serializers import (
    ProductSerializer,
    SingleProductSerializer,
    WhiteGoodsQuantitySerializer,
    WhiteGoodsListSerializer,
    ProductCreateSerializer,
)
from account.serializers import (
    CustomerDisplayAccountSerializer,
    AccountOverviewSerializer,
    NomineeSerializer,
    AccountListAPISerializer,
    AccountListSerializer,
    NomineeDetailsSerializer,
    InsuranceSerializer
)
from account.models import NomineeDetails
from asset.models import Asset
from lender.serializers import LenderSerializer
from users.serializers import UserResponseSerializer, UserSimpleSerializer, UserDetailSerializer
from disbursements.models import Disbursement
import traceback
from utils.responseHandler import HttpResponse
from branch.serializers import (
    CreateBranchSerializer,
    BranchSerializer,
    UpdateBranchSerializer,
)
from utils import helper
from utils.constants import ApplicationType
from branch.models import BranchUserMapping
from asset.serializers import AssetSerializer
from application.models import LoanDocument
from document.serializers import LoanDocumentSerializer
from federal.serializers import ListFederalBankApplicationModelSerializer
from utils.representation_util import RepresentationUtil

class DecimalFieldAsString(serializers.DecimalField):
    """
    Custom DecimalField that serializes to string but deserializes to Decimal.
    """
    def to_representation(self, value):
        # Serialize to string
        return Decimal(value)

    def to_internal_value(self, data):
        # Deserialize to Decimal
        return Decimal(data)


class AddLoanAPISerializer(serializers.ModelSerializer):
    total_asset_price = DecimalFieldAsString(max_digits=10, decimal_places=2)
    total_gross_weight = DecimalFieldAsString(max_digits=10, decimal_places=2)
    total_wastage = DecimalFieldAsString(max_digits=10, decimal_places=2)

    class Meta:
        model = Application
        fields = "__all__"

class AddRequestedAmountAPISerializer(serializers.ModelSerializer):

     class Meta:
        model = Application
        fields = ["purpose_of_loan" , "requested_loan_amount" , "expected_income_increase" , "verify_the_usage"]



class AddGoodsAPISerializer(serializers.ModelSerializer):
    # goods = serializers.SerializerMethodField()
    application_number = serializers.CharField(required=False)
    total_asset_price = DecimalFieldAsString(max_digits=10, decimal_places=2, required=False)
    total_gross_weight = DecimalFieldAsString(max_digits=10, decimal_places=2, required=False)
    total_wastage = DecimalFieldAsString(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Application
        fields = "__all__"

    # def get_goods(self, obj):
    #     goods_data = []
    #     all_agm = ApplicationGoodsMapping.objects.filter(application=obj.application_id)

    #     all_goods_id = [each_agm.goods.goods_id for each_agm in all_agm]
    #     goods_data = WhiteGoods.objects.filter(goods_id__in=all_goods_id)
    #     goods_to_serailize = []
    #     for each_agm in all_agm:
    #         for each_goods in goods_data:
    #             if str(each_agm.goods.goods_id) == str(each_goods.goods_id):
    #                 # for x in range(each_agm.quantity):
    #                 #     goods_to_serailize.append(each_goods)
    #                 # break
    #                 # each_goods["quantity"] = each_agm.quantity
    #                 setattr(
    #                     each_goods, "quantity", each_agm.quantity
    #                 )  # setattr(dict, key, value)
    #                 goods_to_serailize.append(each_goods)

    #     # goods_data = WhiteGoodsSerializer(goods_data, many=True).data
    #     goods_data = WhiteGoodsQuantitySerializer(goods_to_serailize, many=True).data
    #     return goods_data


class ApplicationModelSerializer(serializers.ModelSerializer):
    account = CustomerDisplayAccountSerializer()
    product = ProductSerializer()
    goods = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = "__all__"

    def get_goods(self, obj):
        goods_data = []
        all_agm = ApplicationGoodsMapping.objects.filter(application=obj.application_id)

        all_goods_id = [each_agm.goods.goods_id for each_agm in all_agm]
        goods_data = WhiteGoods.objects.filter(goods_id__in=all_goods_id)
        goods_to_serailize = []
        for each_agm in all_agm:
            for each_goods in goods_data:
                if str(each_agm.goods.goods_id) == str(each_goods.goods_id):
                    # for x in range(each_agm.quantity):
                    #     goods_to_serailize.append(each_goods)
                    # break
                    # each_goods["quantity"] = each_agm.quantity
                    setattr(
                        each_goods, "quantity", each_agm.quantity
                    )  # setattr(dict, key, value)
                    goods_to_serailize.append(each_goods)

        # goods_data = WhiteGoodsSerializer(goods_data, many=True).data
        goods_data = WhiteGoodsQuantitySerializer(goods_to_serailize, many=True).data
        return goods_data


class LoanTakeOverApplicationSerializer(serializers.ModelSerializer):

    application_number = serializers.CharField(required=False)

    class Meta:
        model = Application
        exclude = ['total_asset_price', 'total_gross_weight', 'total_wastage', 'total_goods_price']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        context = self.context
        if len(context) > 0:
            representation["application_number"] = context.get("application_number", 0)
            # representation["total_asset_price"] = float(representation["total_asset_price"])
            # representation["total_gross_weight"] = float(representation["total_gross_weight"])
            # representation["total_wastage"] = float(representation["total_wastage"])

        return representation
    

class CreatApplicationSerializer(serializers.ModelSerializer):

    application_number = serializers.CharField(required=False)
    total_asset_price = DecimalFieldAsString(max_digits=10, decimal_places=2, required=False)
    total_gross_weight = DecimalFieldAsString(max_digits=10, decimal_places=2, required=False)
    total_wastage = DecimalFieldAsString(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Application
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        context = self.context
        if len(context) > 0:
            representation["application_number"] = context.get("application_number", 0)
            # representation["total_asset_price"] = float(representation["total_asset_price"])
            # representation["total_gross_weight"] = float(representation["total_gross_weight"])
            # representation["total_wastage"] = float(representation["total_wastage"])

        return representation


class ApplicationAllSerializer(serializers.ModelSerializer):
    # lender = LenderSerializer()
    class Meta:
        model = Application
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["account"] = AccountListAPISerializer(instance.account).data
        representation["Originatedby"] = UserSimpleSerializer(
            instance.Originatedby
        ).data

        if instance.product:
            representation["product"] = ProductCreateSerializer(instance.product).data
            representation["product"]["lender"] = LenderSerializer(
                instance.product.lender
            ).data
        else:
            representation["product"] = None
        representation["branch"] = CreateBranchSerializer(
            instance.Originatedby.lm_branch_map.all().first().branch
        ).data
        takeover_loans = instance.loan_take_over_app.all()
        if (
            instance.application_type == ApplicationType.TAKEOVER.value
            and takeover_loans.count() > 0
        ):
            representation["requested_amount_from_radian"] = (
                takeover_loans.first().requested_amount_from_radian
            )
        # context = self.context
        # if len(context) > 0:
        #     representation["customer_id"] = context.get("customer_id", 0)

        return representation


class ApplicationGoodsMappingSerializer(serializers.ModelSerializer):
    # quantity = serializers.IntegerField(required=False)

    class Meta:
        model = ApplicationGoodsMapping
        fields = [
            "quantity",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        white_goods_data = WhiteGoodsListSerializer(instance.goods).data
        representation.update(white_goods_data)
        return representation


class ApplicationListSerializer(serializers.ModelSerializer):
    account = AccountListSerializer()
    product = SingleProductSerializer()
    branch = CreateBranchSerializer()
    lender = LenderSerializer()
    total_asset_price = DecimalFieldAsString(max_digits=10, decimal_places=2)
    total_gross_weight = DecimalFieldAsString(max_digits=10, decimal_places=2)
    total_wastage = DecimalFieldAsString(max_digits=10, decimal_places=2)
    loan_documents = serializers.SerializerMethodField()
    Originatedby = UserDetailSerializer()
    show_inspection_screen = serializers.BooleanField(default=False)

    class Meta:
        model = Application
        exclude = (
            # "branch",
            "approvedByBM",
            "approvedByCPC",
            # "Originatedby",
            "live_tracking_id",
            "source_id",
            "approvedByBMAt",
            "approvedByCPCAt",
        )
    
    def get_loan_documents(self, obj):
        try:
            loanDoc = LoanDocument.objects.filter(application=obj)
            return LoanDocumentSerializer(loanDoc, many=True).data
        except Exception as e:
            traceback.print_exc()
            return None


class ApplicationOverviewSerializer(serializers.ModelSerializer):
    account = AccountOverviewSerializer()
    product = SingleProductSerializer()
    insurance_product = InsuranceSerializer(many=False)
    # goods=WhiteGoodsSerializer()
    disbursment_txn = serializers.SerializerMethodField()
    goods = serializers.SerializerMethodField()
    asset = serializers.SerializerMethodField()
    approvedByBM = UserResponseSerializer()
    approvedByCPC = UserResponseSerializer()
    Originatedby = UserResponseSerializer()
    nominee = serializers.SerializerMethodField()
    loan_documents = serializers.SerializerMethodField()
    # lender = LenderSerializer()
    branch = CreateBranchSerializer()
    # branch = serializers.SerializerMethodField()
    # total_asset_price = serializers.SerializerMethodField()
    # total_eligble_amount = serializers.SerializerMethodField()
    # total_net_weight = serializers.SerializerMethodField()
    # total_net_weight_in_22k = serializers.SerializerMethodField()
    # total_wastage = serializers.SerializerMethodField()
    # total_gross_weight = serializers.SerializerMethodField()
    show_inspection_screen = serializers.BooleanField(default=False)
    federal_application = serializers.SerializerMethodField()
    # TODO disbursed_amount=serializers.SerializerMethodField()
    total_asset_price = DecimalFieldAsString(max_digits=10, decimal_places=2)
    total_gross_weight = DecimalFieldAsString(max_digits=10, decimal_places=2)
    total_wastage = DecimalFieldAsString(max_digits=10, decimal_places=2)


    class Meta:
        model = Application
        exclude = ("live_tracking_id", "source_id", "approvedByBMAt", "approvedByCPCAt", "lender")

    def get_federal_application(self, obj):
        try:
            fba = obj.federal_application.all().first()
            return ListFederalBankApplicationModelSerializer(fba).data
        except Exception as e:
            traceback.print_exc()
            return {}

    def get_loan_documents(self, obj):
        try:
            loanDoc = LoanDocument.objects.filter(application=obj)
            return LoanDocumentSerializer(loanDoc, many=True).data
        except Exception as e:
            traceback.print_exc()
            return None

    # def get_total_asset_price(self, obj):
    #     try:
    #         if Asset.objects.filter(application=obj.application_id).exists():
    #             asset = Asset.objects.filter(application=obj.application_id)
    #             total = 0
    #             for i in asseinsurance_product = InsuranceProductSerializer()t:
    #                 total = total + i.asset_price
    #             return total

    #         return None

    #     except Exception as e:
    #         traceback.print_exc()

    # def get_total_eligble_amount(self, obj):
    #     try:
    #         if Asset.objects.filter(application=obj.application_id).exists():
    #             asset = Asset.objects.filter(application=obj.application_id)
    #             total = 0
    #             for i in asset:
    #                 price = (
    #                     float((i.application.product.ltv_percentage))
    #                     / 100
    #                     * float(i.asset_price)
    #                 )
    #                 total = total + price
    #             return round(total, 2)
    #         return None

    #     except Exception as e:
    #         traceback.print_exc()

    # def get_total_net_weight(self, obj):
    #     try:
    #         if Asset.objects.filter(application=obj.application_id).exists():
    #             asset = Asset.objects.filter(application=obj.application_id)
    #             total = 0
    #             for i in asset:
    #                 total = total + i.net_weight
    #             return total
    #         return None
    #     except Exception as e:
    #         traceback.print_exc()

    # def get_total_net_weight_in_22k(self, obj):
    #     try:
    #         if Asset.objects.filter(application=obj.application_id).exists():
    #             asset = Asset.objects.filter(application=obj.application_id)
    #             total = 0
    #             for i in asset:
    #                 weight = helper.customer_gold_weight_converter_to_22_karate_weight(
    #                     i.karat_value, i.net_weight
    #                 )
    #                 total = total + weight
    #             return round(total, 2)

    #         return None
    #     except Exception as e:
    #         traceback.print_exc()

    # def get_total_wastage(self, obj):
    #     try:
    #         if Asset.objects.filter(application=obj.application_id).exists():
    #             asset = Asset.objects.filter(application=obj.application_id)
    #             total = 0
    #             for i in asset:
    #                 total = total + i.wastage
    #             return total
    #         return None
    #     except Exception as e:
    #         traceback.print_exc()

    # def get_total_gross_weight(self, obj):
    #     try:
    #         if Asset.objects.filter(application=obj.application_id).exists():
    #             asset = Asset.objects.filter(application=obj.application_id)
    #             total = 0
    #             for i in asset:
    #                 total = total + i.gross_weight
    #             return total
    #         return None
    #     except Exception as e:
    #         traceback.print_exc()

    # def get_disbursed_amount(self,obj):
    #     try :

    #         if Loan.objects.filter(application=obj.application_id).exists():
    #             amount=Loan.objects.filter(application=obj.application_id)[0]
    #             if amount:
    #                 return amount.disbursed_amount
    #         return None
    #     except Exception as e:
    #         traceback.print_exc()
    #         return HttpResponse.InternalServerError(str(e))

    # def get_branch(self, obj):
    #     try:

    #         branch = BranchUserMapping.objects.filter(user=obj.Originatedby).first()
    #         if branch:
    #             return CreateBranchSerializer(branch.branch).data
    #         return None
    #     except Exception as e:
    #         traceback.print_exc()
    #         return HttpResponse.InternalServerError(str(e))

    def get_goods(self, obj):
        goodsMapping = obj.agmMap_application.all()
        return ApplicationGoodsMappingSerializer(goodsMapping, many=True).data
    
        # goods_data = []
        # all_agm = ApplicationGoodsMapping.objects.filter(application=obj.application_id)

        # all_goods_id = [each_agm.goods.goods_id for each_agm in all_agm]
        # goods_data = WhiteGoods.objects.filter(goods_id__in=all_goods_id)
        # goods_to_serailize = []
        # for each_agm in all_agm:
        #     for each_goods in goods_data:
        #         if str(each_agm.goods.goods_id) == str(each_goods.goods_id):
        #             # for x in range(each_agm.quantity):
        #             #     goods_to_serailize.append(each_goods)
        #             # break
        #             # each_goods["quantity"] = each_agm.quantity
        #             setattr(
        #                 each_goods, "quantity", each_agm.quantity
        #             )  # setattr(dict, key, value)
        #             goods_to_serailize.append(each_goods)

        # # goods_data = WhiteGoodsSerializer(goods_data, many=True).data
        # goods_data = WhiteGoodsQuantitySerializer(goods_to_serailize, many=True).data
        # return goods_data

    def get_disbursment_txn(self, obj):
        disbursments = Disbursement.objects.filter(application=obj.application_id)
        return DisbursementSerializer(disbursments, many=True).data

    def get_asset(self, obj):
        try:
            assets = obj.asset_application.all()
            return AssetSerializer(assets, many=True).data
            # if Asset.objects.filter(application=obj.application_id).exists():
            #     asset = Asset.objects.filter(application=obj.application_id)
            #     if asset:
            #         return AssetSerializer(asset, many=True).data
            # return None
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def get_nominee(self, obj):
        try:
            nominee = NomineeDetails.objects.filter(account=obj.account)
            if len(nominee) > 0:
                return NomineeDetailsSerializer(nominee[0]).data
            return None
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class CustomerDashboardSerializer(serializers.ModelSerializer):

    loan_id = serializers.CharField()
    days_past_due = serializers.IntegerField(allow_null=True)
    interest_accrued_till_date = serializers.IntegerField(allow_null=True)
    loan_status = serializers.CharField()
    loan_number = serializers.CharField()
    loan_disbursed_date = serializers.DateTimeField()

    class Meta:
        model = Application
        fields = [
            "application_id",
            "branch",
            "product",
            "lender",
            "loan_amount",
            "tenure",
            "net_weight",
            "loan_id",
            "days_past_due",
            "interest_accrued_till_date",
            "application_number",
            "loan_status",
            "loan_number",
            "loan_disbursed_date",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["product"] = ProductCreateSerializer(instance.product).data
        representation["lender"] = LenderSerializer(instance.lender).data
        representation["branch"] = UpdateBranchSerializer(instance.branch).data
        return representation


class LoanDaraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"


class CustomerApplicationDetailsSerializer(serializers.ModelSerializer):

    loan = LoanDaraSerializer(source="loan_application", many=True)
    loan_documents = serializers.SerializerMethodField()
    goods = serializers.SerializerMethodField()
    asset = serializers.SerializerMethodField()
    approvedByBM = UserResponseSerializer()
    approvedByCPC = UserResponseSerializer()
    Originatedby = UserResponseSerializer()
    nominee = serializers.SerializerMethodField()
    lender = LenderSerializer()
    branch = serializers.SerializerMethodField()
    total_asset_price = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = "__all__"

    def get_loan_documents(self, obj):
        try:
            loanDoc = LoanDocument.objects.filter(application=obj)
            return LoanDocumentSerializer(loanDoc, many=True).data
        except Exception as e:
            traceback.print_exc()
            return None

    def get_total_asset_price(self, obj):
        try:
            if Asset.objects.filter(application=obj.application_id).exists():
                asset = Asset.objects.filter(application=obj.application_id)
                total = 0
                for i in asset:
                    total = total + i.asset_price
                return total

            return None

        except Exception as e:
            traceback.print_exc()

    def get_total_eligble_amount(self, obj):
        try:
            if Asset.objects.filter(application=obj.application_id).exists():
                asset = Asset.objects.filter(application=obj.application_id)
                total = 0
                for i in asset:
                    price = (
                        float((i.application.product.ltv_percentage))
                        / 100
                        * float(i.asset_price)
                    )
                    total = total + price
                return round(total, 2)
            return None

        except Exception as e:
            traceback.print_exc()

    def get_total_net_weight(self, obj):
        try:
            if Asset.objects.filter(application=obj.application_id).exists():
                asset = Asset.objects.filter(application=obj.application_id)
                total = 0
                for i in asset:
                    total = total + i.net_weight
                return total
            return None
        except Exception as e:
            traceback.print_exc()

    # def get_total_net_weight_in_22k(self, obj):
    #     try:
    #         if Asset.objects.filter(application=obj.application_id).exists():
    #             asset = Asset.objects.filter(application=obj.application_id)
    #             total = 0
    #             for i in asset:
    #                 weight = helper.customer_gold_weight_converter_to_22_karate_weight(
    #                     i.karat_value, i.net_weight
    #                 )
    #                 total = total + weight
    #             return round(total, 2)

    #         return None
    #     except Exception as e:
    #         traceback.print_exc()

    def get_total_wastage(self, obj):
        try:
            if Asset.objects.filter(application=obj.application_id).exists():
                asset = Asset.objects.filter(application=obj.application_id)
                total = 0
                for i in asset:
                    total = total + i.wastage
                return total
            return None
        except Exception as e:
            traceback.print_exc()

    def get_total_gross_weight(self, obj):
        try:
            if Asset.objects.filter(application=obj.application_id).exists():
                asset = Asset.objects.filter(application=obj.application_id)
                total = 0
                for i in asset:
                    total = total + i.gross_weight
                return total
            return None
        except Exception as e:
            traceback.print_exc()

        # def get_disbursed_amount(self,obj):
        #     try :

        #         if Loan.objects.filter(application=obj.application_id).exists():
        #             amount=Loan.objects.filter(application=obj.application_id)[0]
        #             if amount:
        #                 return amount.disbursed_amount
        #         return None
        #     except Exception as e:
        #         traceback.print_exc()
        #         return HttpResponse.InternalServerError(str(e))

    def get_branch(self, obj):
        try:

            branch = BranchUserMapping.objects.filter(user=obj.Originatedby).first()
            if branch:
                return CreateBranchSerializer(branch.branch).data
            return None
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def get_goods(self, obj):
        goods_data = []
        all_agm = ApplicationGoodsMapping.objects.filter(application=obj.application_id)

        all_goods_id = [each_agm.goods.goods_id for each_agm in all_agm]
        goods_data = WhiteGoods.objects.filter(goods_id__in=all_goods_id)
        goods_to_serailize = []
        for each_agm in all_agm:
            for each_goods in goods_data:
                if str(each_agm.goods.goods_id) == str(each_goods.goods_id):
                    # for x in range(each_agm.quantity):
                    #     goods_to_serailize.append(each_goods)
                    # break
                    # each_goods["quantity"] = each_agm.quantity
                    setattr(
                        each_goods, "quantity", each_agm.quantity
                    )  # setattr(dict, key, value)
                    goods_to_serailize.append(each_goods)

        # goods_data = WhiteGoodsSerializer(goods_data, many=True).data
        goods_data = WhiteGoodsQuantitySerializer(goods_to_serailize, many=True).data
        return goods_data

    def get_disbursment_txn(self, obj):
        disbursments = Disbursement.objects.filter(application=obj.application_id)
        return DisbursementSerializer(disbursments, many=True).data

    def get_asset(self, obj):
        try:
            if Asset.objects.filter(application=obj.application_id).exists():
                asset = Asset.objects.filter(application=obj.application_id)
                if asset:
                    return AssetSerializer(asset, many=True).data
            return None
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def get_nominee(self, obj):
        try:
            if NomineeDetails.objects.filter(account=obj.account).exists():
                nominee = NomineeDetails.objects.filter(account=obj.account)[0]
                if nominee:
                    return NomineeDetailsSerializer(nominee).data
            return None
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        

class ApplicationHistorySerializer(serializers.ModelSerializer):
    history_type = serializers.SerializerMethodField()
    history_date = serializers.DateTimeField()
    history_user = serializers.CharField()
    history_user_id = serializers.UUIDField()
    changes = serializers.SerializerMethodField()
    
    def get_history_type(self, obj):
        history_type_mapping = {
            '+': 'Created',
            '~': 'Updated',
            '-': 'Deleted',
        }
        # Get the label from the mapping, defaulting to the original value if not found
        return history_type_mapping.get(obj.history_type, obj.history_type)

    class Meta:
        model = Application.history.model
        fields = ('history_date', 'history_user', 'changes', 'history_type', 'history_user_id')

    def get_changes(self, obj):
        prev_record = obj.prev_record
        changes = {}

        if prev_record:
            # Iterate over the fields of the original model
            for field in obj.instance._meta.fields:
                # Skip "modified_at" and "modified_by" fields
                if field.name in ["modified_at", "modified_by"]:
                    continue
                old_value = getattr(prev_record, field.attname)
                new_value = getattr(obj, field.attname)

                # Check if the field value has changed
                if old_value != new_value:
                    changes[field.name] = new_value

        return changes
    
class ApplicationWithHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = "__all__"
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["history"] = self.context.get("history")
        utils = RepresentationUtil(representation)
        representation = utils.change_all()
        return representation
    
class ApplicationDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = "__all__"


class NewApplicationSerializer(serializers.ModelSerializer):
    onboarding_application_id = serializers.CharField(
        source="onboarding_application.application_id",
        read_only=True,
    )
    customer_id = serializers.SerializerMethodField()

    class Meta:
        model = NewApplication
        fields = "__all__"

    def validate(self, attrs):
        account = attrs.get("account", getattr(self.instance, "account", None))
        onboarding_application = attrs.get(
            "onboarding_application",
            getattr(self.instance, "onboarding_application", None),
        )

        if not account and not onboarding_application:
            raise serializers.ValidationError(
                "Either account or onboarding_application is required."
            )

        if account and onboarding_application:
            account_lead_id = getattr(account, "lead_id", None)
            application_lead_id = getattr(onboarding_application, "lead_id", None)
            if account_lead_id and application_lead_id and account_lead_id != application_lead_id:
                raise serializers.ValidationError(
                    "account and onboarding_application must belong to the same lead."
                )

        return attrs

    def get_customer_id(self, obj):
        if obj.account_id:
            return getattr(obj.account, "customer_id", None)
        if obj.onboarding_application_id:
            return getattr(obj.onboarding_application.lead, "customer_id", None)
        return None
