"""All account related serializers goes here"""

from rest_framework import serializers
from .models import Account, BankAccount, NomineeDetails, InsuranceProduct, AgentAccount, AgentBankAccount ,NewAccountDocument, NewAccount
from credit_status.models import CreditStatus
from reference_pd.models import Reference_PD
from reference_pd.serializer import Reference_PDSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from users.serializers import UserResponseSerializer, UserSimpleSerializer
from document.models import Document
from document.serializers import (
    DocumentDisplaySerializer,
    DocumentDisplayOverviewSerializer,
    DocumentSerializer,
    FileLinkSerializer,
)
from utils.constants import DOCUMENT_TYPE, FRS_DOC_VERIFY,APPLICANT_TYPE
from users.serializers import AddressesDisplaySerializer

import traceback
from utils.representation_util import RepresentationUtil
from datetime import datetime

class AccountListAPISerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ["profile_photo", "user"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["profile_photo"] = FileLinkSerializer(
            instance.profile_photo
        ).data
        representation["user"] = UserSimpleSerializer(instance.user).data
        return representation


class AccountCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["profile_photo"] = DocumentDisplaySerializer(
            Document.objects.get(document_id=representation["profile_photo"])
        ).data
        return representation


class CreateAccountRequestSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    profile_photo = serializers.FileField()
    lead_id = serializers.CharField(required=False)
    customer_id = serializers.CharField(required=False)

    # lead=serializers.SerializerMethodField()
    class Meta:
        model = Account
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        context = self.context
        if len(context) > 0:
            representation["customer_id"] = context.get("customer_id", 0)

        return representation


# class AccountModelSerializer(serializers.ModelSerializer):
#     profile_photo = DocumentDisplaySerializer()


#     class Meta:
#         model = Account
#         fields = "__all__"
class AccountModelSerializer(serializers.ModelSerializer):
    profile_photo = DocumentDisplaySerializer()
    user = UserResponseSerializer()
    created_by = UserResponseSerializer()
    applicant = UserResponseSerializer()

    class Meta:
        model = Account
        exclude = (
            "branch",
            "insurance_product",
        )


class CustomerDisplayAccountSerializer(serializers.ModelSerializer):
    user = UserResponseSerializer()
    created_by = UserResponseSerializer()
    profile_photo = DocumentDisplaySerializer()

    class Meta:
        model = Account
        exclude = (
            "aadhar_meta_field",
            "pan_meta_field",
        )
        # fields = ("title", "gender", "year_of_birth", "occupation_status","user","created_by", "created_at", "modefied_at")

        # def update(self, instance, validated_data):
        #     instance.name = validated_data.get('name', instance.name)
        #     instance.phone = validated_data.get('phone', instance.phone)
        #     instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        #     instance.email = validated_data.get('email', instance.email)
        #     instance.address = validated_data.get('address', instance.address)
        #     instance.adhar_number = validated_data.get('adhar_number', instance.adhar_number)
        #     instance.pan_number = validated_data.get('pan_number', instance.pan_number)
        #     user=User.objects.filter(phone=instance.phone).first()
        #     if user:
        #         instance.user = user

        #     instance.save()
        #     print("Created instance")
        #     return instance

    # def to_representation(self, instance):
    #     representation = super(CustomerAccountSerializer,self).to_representation(instance)
    #     # representation = instance.to_representation(instance)
    #     representation["user"]=UserResponseSerializer(instance.account_user.all(),many=True)
    #     return representation


class NomineeSerializer(serializers.ModelSerializer):
    # account = AccountModelSerializer()

    class Meta:
        model = NomineeDetails
        fields = "__all__"
        # fields = (
        #     "account_number",
        #     "bank_name",
        #     "ifsc",
        #     "account",
        #     "account_holder_name",
        # )
        #     instance.save()
        #     print("Created instance")
        #     return instance


class BankAccountPostSerializer(serializers.ModelSerializer):
    # account = AccountModelSerializer()
    # bank_document=serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = "__all__"


class BankAccountSerializer(serializers.ModelSerializer):
    # account = AccountModelSerializer()
    # bank_document=serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = "__all__"
        # fields = (
        #     "account_number",
        #     "bank_name",
        #     "ifsc",
        #     "account",
        #     "account_holder_name",
        # )
        #     instance.save()
        #     print("Created instance")
        #     return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["account"] = AccountModelSerializer(instance.account).data
        try:

            document = Document.objects.filter(account=instance.account)
            try:
                document = document.get(document_type="BANK_PASSBOOK") or document.get(
                    document_type="CHEQUE_BOOK"
                )
                if document:
                    representation["bank_documents"] = DocumentSerializer(document).data
                else:
                    representation["bank_documents"] = None
                return representation
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)


class AccountListSerializer(serializers.ModelSerializer):
    # profile_photo = serializers.SerializerMethodField()
    profile_photo = FileLinkSerializer()
    # bankaccount = BankAccountPostSerializer(many=True, source="bankaccount_account")
    # documents = DocumentDisplayOverviewSerializer(many=True, source="document_account")
    # address = AddressesDisplaySerializer(many=True, source="user_addresse")
    user = UserSimpleSerializer()

    class Meta:
        model = Account
        fields = [
            "account_id",
            "customer_id",
            "insurance_product",
            "insurance_amount",
            "insurance_amount_covered_from",
            "user",
            "year_of_birth",
            "profile_photo",
        ]

    # def get_profile_photo(self, obj):
    #     try:
    #         print("obj.profile_photo: ", obj.profile_photo.file)
    #         return {
    #             "file": obj.profile_photo.file
    #         }
    #     except Exception as e:
    #         traceback.print_exc()
    #         return {}


class AccountOverviewSerializer(serializers.ModelSerializer):
    profile_photo = DocumentDisplaySerializer()
    bankaccount = BankAccountPostSerializer(many=True, source="bankaccount_account")
    documents = DocumentDisplayOverviewSerializer(many=True, source="document_account")
    address = AddressesDisplaySerializer(many=True, source="user_addresse")
    user = UserResponseSerializer()

    class Meta:
        model = Account
        exclude = (
            "aadhar_meta_field",
            "pan_meta_field",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        context = self.context
        if len(context) > 0:
            representation["address"] = context.get("address", 0)

        if instance.user:
            co_applicants = Account.objects.filter(
                applicant=instance.user.user_id, 
                applicant_type=APPLICANT_TYPE.CO_APPLICANT.value
            )


            # Serialize only if co-applicants exist
            representation["co_applicants"] = AccountOverviewSerializer(co_applicants, many=True).data
        else:
            representation["co_applicants"] = []  # Empty list if no applicant is present

        return representation


class VerifySerializer(serializers.Serializer):
    doc_type = serializers.ChoiceField(
        choices=[(e.value, e.value) for e in FRS_DOC_VERIFY]
    )
    account_id = serializers.UUIDField(required=False, allow_null=True)
    verification_id = serializers.CharField(
        max_length=100, allow_null=True, required=False
    )
    data = serializers.JSONField(allow_null=True, required=False)


class EsignSerializer(serializers.Serializer):
    sender = serializers.CharField(max_length=100)
    signatory = serializers.CharField(max_length=100)
    signature_config = serializers.CharField(max_length=100)
    reminder_config = serializers.CharField(max_length=100)
    document_config = serializers.CharField(max_length=100)
    document = serializers.FileField()


class VerificationUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = [
            "aadhar_no",
            "pan_no",
            "aadhar_meta_field",
            "pan_verified",
            "aadhar_verified",
        ]


class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceProduct
        fields = "__all__"


class AccountWithInsuranceSerializer(serializers.ModelSerializer):
    insurance_product = InsuranceSerializer(many=False)

    class Meta:
        model = Account
        fields = [
            "insurance_product",
            "insurance_amount",
            "insurance_amount_covered_from",
        ]


class NomineeDetailsSerializer(serializers.ModelSerializer):
    insurance_policy_selected = InsuranceSerializer(many=False)

    class Meta:
        model = NomineeDetails
        exclude = ("aadhar_meta_field",)



class AccountHistorySerializer(serializers.ModelSerializer):
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
        model = Account.history.model
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
    
class AccountWithHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = "__all__"
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["history"] = self.context.get("history")
        utils = RepresentationUtil(representation)
        representation = utils.change_all()
        return representation
    

class WellnessNomineeDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NomineeDetails
        fields = '__all__'

    def validate(self, data):
        # Calculate age from year_of_birth
        date_of_birth = data.get('date_of_birth')
        if date_of_birth:
            today = datetime.today()
            data['age'] = today.year - date_of_birth.year
        return data


class AgentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentAccount
        fields = "__all__"
        read_only_fields = ('created_by', 'modified_by', 'created_at', 'modified_at')


class AgentBankAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgentBankAccount
        fields = "__all__"

class NewAccountDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = NewAccountDocument
        fields = [
            "document_id",
            "document_type",
            "file_name",
            "file",
            "file_url",
            "status",
            "source",
            "uploaded_by",
            "created_at",
        ]

    def get_file_url(self, obj):
        return obj.get_file_url()


class NewAccountSerializer(serializers.ModelSerializer):
    documents = NewAccountDocumentSerializer(source="new_account_document", many=True, read_only=True)

    class Meta:
        model = NewAccount
        fields = "__all__"
        read_only_fields = ["new_account_id","is_pan_verified"]




