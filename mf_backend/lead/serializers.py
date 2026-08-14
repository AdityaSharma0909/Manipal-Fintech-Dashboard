from rest_framework import serializers
from rest_framework.permissions import AllowAny
from .models import Lead , LeadDocument , NewLead

from users.models import User
from users.serializers import (
    UserResponseSerializer,
    LeaderBoardSerializer,
    UserFieldSerializer,
)
from document.serializers import LeadDocumentSerializer
from account.models import Account
from account.serializers import CustomerDisplayAccountSerializer, AccountModelSerializer ,AccountOverviewSerializer
from users.serializers import TimeStampSerializer
from lender.serializers import LenderSerializer
from django.core.exceptions import ObjectDoesNotExist
from utils.constants import LENDING_TYPE, APPLICANT_TYPE

class LeadDisplaySerializer(serializers.ModelSerializer):
    assigned_to = UserResponseSerializer()
    created_by = UserFieldSerializer()
    account = CustomerDisplayAccountSerializer()
    lender = LenderSerializer()
    documents = LeadDocumentSerializer(many=True, source='lead_document', read_only=True)

    class Meta:
        model = Lead
        fields = "__all__"

    def to_representation(self, instance):
        # Get the original serialized data
        data = super().to_representation(instance)
        # Add lender_name to the response
        data['lender_name'] = instance.lender.lender_name if instance.lender else None
        if instance.account:
            co_applicants = Account.objects.filter(
                applicant=instance.account.user.user_id, 
                applicant_type=APPLICANT_TYPE.CO_APPLICANT.value
            )


            # Serialize only if co-applicants exist
            data["co_applicants"] = CustomerDisplayAccountSerializer(co_applicants, many=True).data
        else:
            data["co_applicants"] = []  # Empty list if no applicant is present

        
        return data


class LeadAllDisplaySerializer(serializers.ModelSerializer):
    assigned_to = UserFieldSerializer()
    created_by = UserFieldSerializer()
    account = CustomerDisplayAccountSerializer()
    lender = LenderSerializer()

    class Meta:
        model = Lead
        fields = "__all__"
    
    


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"

    # def to_representation(self, instance):
    #     instance =super().to_representation(instance)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        createdUser = User.objects.get(user_id=representation["created_by"])
        # assignedUser = User.objects.get(user_id=representation["assigned_to"])
        representation["created_by"] = UserResponseSerializer(createdUser).data
        # representation["assigned_to"] = UserResponseSerializer(assignedUser).data
        try:
            assignedUser = User.objects.get(user_id=representation["assigned_to"])
            representation["assigned_to"] = UserResponseSerializer(assignedUser).data
        except (ObjectDoesNotExist, TypeError):
            representation["assigned_to"] = None
            
        return representation



class LeadResponseSerializer(serializers.ModelSerializer):
    account = AccountModelSerializer()
    created_by = UserResponseSerializer()
    assigned_to = UserResponseSerializer()

    class Meta:
        model = Lead
        fields = "__all__"

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     createdUser = User.objects.get(user_id=representation["created_by"])
    #     assignedUser = User.objects.get(user_id=representation["assigned_to"])
    #     representation["created_by"] = UserResponseSerializer(createdUser).data
    #     representation["assigned_to"] = UserResponseSerializer(assignedUser).data
    #     return representation


class OpenLeadSerializer(serializers.ModelSerializer):
    verification_token = serializers.UUIDField(required=False, allow_null=True)

    class Meta:
        model = Lead
        fields = [
            "first_name",
            "last_name",
            "address_line",
            "pincode",
            "city",
            "state",
            "country",
            "phone",
            "is_phone_verified",
            "verification_token",
            "comments",
            "latitude",
            "longitude",
            "email",
            "source",
        ]
        extra_kwargs = {
            "verification_token": {
                "read_only": True,
                "required": False,
                "allow_null": True,
            },
            "is_phone_verified": {
                "required": False,
            },
        }

    def create(self, validated_data):
        validated_data.pop("verification_token", None)
        validated_data['is_phone_verified'] = True
        print("validated_data: ", validated_data)
        return super().create(validated_data)
    
    def to_representation(self, instance):
        result = super().to_representation(instance)
        result.pop("verification_token")
        return result


# class LeaderBoard(serializers.Serializer):
#     name = serializers.SerializerMethodField()
#     disbursed_amount=serializers.SerializerMethodField()
#     def get_name(self, obj):
#         user=User.objects.get(username=str(obj[0]))

#         return UserFieldSerializer(user).data
#     def get_disbursed_amount(self,obj):
#         print(obj[1]["disbursed_amount__sum"])
#         return obj[1]["disbursed_amount__sum"]


class DashboardSerializer(serializers.Serializer):
    total_no_of_leads = serializers.IntegerField()
    total_account_created = serializers.IntegerField()
    leads_to_be_covered = serializers.IntegerField()
    total_loan_amount = serializers.IntegerField()
    total_application_created = serializers.IntegerField()
    total_disbursed_amount = serializers.IntegerField()
    total_application_assets_net_weight = serializers.IntegerField()
    total_loan_created = serializers.IntegerField()
    # leaderboard = LeaderBoardSerializer(many=True)
    timestamps = TimeStampSerializer(many=True)
    gold_rate_per_gram = serializers.FloatField()
    lending_gold_rate_per_gram = serializers.FloatField()
    # recent_apps = serializers.JSONField()
    # recent_accounts = serializers.JSONField()


class AxisBankSerializer(serializers.Serializer):
    first_name=serializers.CharField(max_length=100)
    last_name=serializers.CharField(max_length=100)
    city=serializers.CharField(max_length=100)
    state=serializers.CharField(max_length=100)
    email=serializers.CharField(max_length=100)
    address1=serializers.CharField(max_length=100)
    address2=serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    address3=serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    dob=serializers.CharField(max_length=100)
    mobile_number=serializers.CharField(max_length=100)


class ReferedLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            "first_name",
            "last_name",
            "address_line",
            "phone",
            "email",
            "source",
            "refered_by",
            "created_at",
            "modified_at"
        ]


class NewLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewLead
        fields = "__all__"


