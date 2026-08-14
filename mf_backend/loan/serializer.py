from rest_framework import serializers
from asset.models import Asset
from lender.serializers import LenderSerializer
from .models import Loan, LoanEMISchedule, LoanEMIRecord, LiveTracking, OtherLenderApprainsal, GprsPhotos
from application.serializers import ApplicationModelSerializer 
from phonenumber_field.serializerfields import PhoneNumberField
from users.serializers import UserResponseSerializer
from users.models import User
from asset.models import Asset
from asset.serializers import AssetSerializer

from disbursements.models import Disbursement
import traceback

from .services.loan_emi_record_service import LoanEmiService
from utils.constants import PHOTO_TYPE


class CollectGoldOtpSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    username = serializers.CharField()
   

class VerifyGoldOtpSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    otp = serializers.CharField(max_length=8)



class LoanSerializer(serializers.ModelSerializer):
    loan_number=serializers.CharField(required=False)
    #disbursed_amount=serializers.SerializerMethodField()
    #lender=LenderSerializer(read_only=True, required=False, allow_null=True)
    class Meta:
        model = Loan
        fields="__all__"

    def save(self, **kwargs):
        try:
            loan=Loan(**self.validated_data)
            loan.save()
            LoanEmiService().update_loan(self.validated_data.get('application'), loan)
            self.validated_data['loan_id']=loan.loan_id
            return self.validated_data
        except Exception:
            traceback.print_exc()


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        context=self.context
        if len(context) >0:
            representation['loan_number']=context.get('loan_number',0)
            
        return representation
    # def get_disbursed_amount(self,obj):
    #     try :
    #
    #         if Disbursement.objects.filter(loan=obj.loan_id).exists():
    #             amount=Disbursement.objects.filter(loan=obj.loan_id)[0]
    #             if amount:
    #                 return amount.disbursed_amount
    #             else :
    #                 return None
    #     except Exception as e:
    #         traceback.print_exc()
    #         return None


class LoanResponseSerializer(serializers.ModelSerializer):
    loan_number = serializers.CharField(required=False)
    disbursed_amount = serializers.SerializerMethodField()
    lender = LenderSerializer(read_only=True, required=False, allow_null=True)

    class Meta:
        model = Loan
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        context = self.context
        if len(context) > 0:
            representation['loan_number'] = context.get('loan_number', 0)

        return representation

    def get_disbursed_amount(self, obj):
        try:

            if Disbursement.objects.filter(loan=obj.loan_id).exists():
                amount = Disbursement.objects.filter(loan=obj.loan_id)[0]
                if amount:
                    return amount.disbursed_amount
                else:
                    return None
        except Exception as e:
            traceback.print_exc()
            return None



class LoanEMIHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanEMISchedule
        fields="__all__"

class LoanEMIRecordSerializer(serializers.ModelSerializer):
    loan_emi_header=LoanEMIHeaderSerializer()
    class Meta:
        model = LoanEMIRecord
        fields="__all__"

class LiveTrackingSerializer(serializers.Serializer):
    loan=LoanSerializer()
    loan_manager=LoanSerializer()
    customer=UserResponseSerializer()
    
    class Meta:
        model = LiveTracking
        fields="__all__"


class OtherLenderAppraisalSerializer(serializers.ModelSerializer):
    # created_by= UserResponseSerializer()
    
    class Meta:
        model = OtherLenderApprainsal
        fields="__all__"

    def to_representation(self, instance):
        representation=super().to_representation(instance)
        representation['created_by'] = UserResponseSerializer(User.objects.get(user_id=representation['created_by'])).data
        return representation


class GPRSDocSerializer(serializers.ModelSerializer):

    class Meta:
        model=GprsPhotos
        fields='__all__'

class GPRSDocOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = GprsPhotos
        fields = '__all__'

    def to_representation(self, instance):
        # Define photo types to always include
        always_include_photo_types = [
            PHOTO_TYPE.IMAGE_OF_HOUSE_WITH_PERSON_STANDING_AT_THE_GATE.value,
            PHOTO_TYPE.IMAGE_OF_SHOP_WITH_PERSON_STANDING_AT_THE_GATE.value,
            PHOTO_TYPE.IMAGE_OF_INSIDE_THE_SHOP.value,
            PHOTO_TYPE.OTHERS.value
        ]

        # Define photo types to include only if application_id matches
        conditional_photo_types = [
            PHOTO_TYPE.CO_IMAGE_OF_HOUSE_WITH_PERSON_STANDING_AT_THE_GATE.value,
            PHOTO_TYPE.CO_IMAGE_OF_SHOP_WITH_PERSON_STANDING_AT_THE_GATE.value,
            PHOTO_TYPE.CO_IMAGE_OF_INSIDE_THE_SHOP.value,
            PHOTO_TYPE.CO_OTHERS.value
        ]

        # Access the application_id from API parameters (via request context)
        request = self.context.get('request')
        application_id = request.query_params.get('application_id') if request else None

        if instance.photo_type in always_include_photo_types:
            return super().to_representation(instance)

        if (
            instance.photo_type in conditional_photo_types and 
            str(instance.application_id) == str(application_id)
        ):
            return super().to_representation(instance)

        return None



class LoanAllSerializer(serializers.ModelSerializer):
    application=ApplicationModelSerializer()
    Originatedby= UserResponseSerializer()
    other_lender_appraisal = OtherLenderAppraisalSerializer()
    class Meta:
        model = Loan
        fields="__all__"

    def to_representation(self, instance):
        representation=super().to_representation(instance)
        # representation['assets']=Asset.objects.values()\
        #     .filter(application__application_id=representation['application']['application_id'])
        return representation
    
class LoanHistorySerializer(serializers.ModelSerializer):
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
        model = Loan.history.model
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
    
class LoanWithHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = "__all__"
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["history"] = self.context.get("history")
        return representation
    
class LoanAssetSerializer(serializers.ModelSerializer):
    application = ApplicationModelSerializer()
    Originatedby = UserResponseSerializer()
    other_lender_appraisal = OtherLenderAppraisalSerializer()

    class Meta:
        model = Loan
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Retrieve assets related to the loan's application
        assets = Asset.objects.filter(application__application_id=representation['application']['application_id'])
        
        # Serialize the assets using AssetSerializer
        asset_serializer = AssetSerializer(instance=assets, many=True)
        serialized_assets = asset_serializer.data
        
        representation['assets'] = serialized_assets
        
        return representation