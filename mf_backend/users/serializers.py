from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import User, Address, UserDeviceDetails, TimeStamp
from dateutil import parser as parser
from users.selfie_urls import get_selfie_access_url
from utils.constants import ROLES


class UserModelSerializer(serializers.ModelSerializer):
    assign_so = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = User
        exclude = ["password"]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = instance.assign_so
        if user:
            data['assign_so'] = {
                "user_id": str(user.user_id),
                "employee_id": user.employee_id,
                "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                "city": user.city,
            }
        else:
            data['assign_so'] = None
        return data



class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone", "first_name", "last_name")


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ('username', 'phone', 'first_name', 'last_name', 'role')
        fields = (
            "phone",
            "first_name",
            "last_name",
            "user_id",
            "role",
            "employee_id",
            "email",
        )


class UserResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "user_id",
            "username",
            "first_name",
            "last_name",
            "phone",
            "role",
            # "aadhar_no",
            "designation",
            "pan_no",
            "employee_id",
            "date_of_joining",
            "exclude_from_bt_date_logic",
            "email",
            "is_active",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation["date_of_joining"] is not None:
            representation["date_of_joining"] = parser.parse(
                representation["date_of_joining"]
            )
        return representation


class LeaderBoardSerializer(serializers.ModelSerializer):
    total_disbursed_amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = User
        fields = (
            "user_id",
            "username",
            "first_name",
            "last_name",
            "phone",
            "role",
            "total_disbursed_amount",
        )


class UserFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "phone", "role")


class TimeStampSerializer(serializers.ModelSerializer):
    selfie = serializers.SerializerMethodField()

    class Meta:
        model = TimeStamp
        fields = "__all__"

    def get_selfie(self, obj):
        return get_selfie_access_url(obj.selfie)


class GenerateOtpSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    username = serializers.CharField()
    platform = serializers.ChoiceField(choices=['web', 'phone'], required=False)

class AgentGenerateOtpSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    platform = serializers.ChoiceField(choices=['web', 'phone'], required=False)



class CustomerGenerateOtpSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    platform = serializers.ChoiceField(choices=['web', 'phone'], required=False)


class VerifyOtpSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    otp = serializers.CharField(max_length=8)
    platform = serializers.ChoiceField(choices=['web', 'phone'], required=False)


class ForgotPasswordRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)


class ForgotPasswordVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=8)


class ForgotPasswordResetSerializer(serializers.Serializer):
    verification_token = serializers.UUIDField()
    new_password = serializers.CharField(min_length=8)


class LoginVerifySerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    platform = serializers.ChoiceField(choices=['web', 'phone'], required=False)


class AddressesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class AddressesDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


# class BothAddressSerializer(serializers.Serializer):
#     permenant_address = serializers.ListField(child=AddressesSerializer)
#     corrospondence_address = serializers.ListField(child=AddressesSerializer)


class UserDeviceDetailsModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDeviceDetails
        fields = "__all__"


# class UserUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             "user_id",
#             "username",
#             "first_name",
#             "last_name",
#             "phone",
#             "role",
#             "aadhar_no",
#             "designation",
#             "pan_no",
#             "employee_id",
#             "date_of_joining",
#             "email",
#             "is_active",
#             "employee_profile_photo",
#         )
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "user_id",
            "username",
            "first_name",
            "last_name",
            "phone",
            "role",
            "aadhar_no",
            "designation",
            "pan_no",
            "employee_id",
            "date_of_joining",
            "exclude_from_bt_date_logic",
            "email",
            "is_active",
            "employee_profile_photo",

            # ✅ ADD THESE FIELDS
            "state",
            "district",
            "city",
            "pincode",
            "team",
            "badge",
            "assign_so",
        )

    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", None))
        excluded = attrs.get(
            "exclude_from_bt_date_logic",
            getattr(self.instance, "exclude_from_bt_date_logic", False),
        )
        if excluded and role != ROLES.SALES_OFFICER.value:
            raise serializers.ValidationError({
                "exclude_from_bt_date_logic": "This exception is only available for Sales Officer users."
            })
        return attrs


class RememberMeSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=256)
    password = serializers.CharField(max_length=256)
