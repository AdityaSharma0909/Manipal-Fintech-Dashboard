import uuid
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

from users.service.password_service import PasswordService
from utils.constants import ROLES, ADDRESS_TYPE, PLATFORM_TYPE, RESENDITIAL_OWNERSHIP, OTP_TYPE, TEAM, DESIGNATION

# from account.models import Account
from django.db.models import UniqueConstraint
from utils.constants import TIMESTAMP
from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.validators import RegexValidator


class User(AbstractUser):
    # user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # username = models.CharField(max_length=100)
    # password = models.CharField(max_length=128, null=True, blank=True)
    # email = models.EmailField(max_length=256, null=True, blank=True ,default=False)
    # phone = PhoneNumberField(null=True, blank=True)
    # role=models.CharField( choices=[(e.value, e.value) for e in ROLES],max_length=12)

    # is_active = models.BooleanField(default=True)
    # is_admin = models.BooleanField(default=False)

    # objects = UserManager()

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username', 'password','phone','role'],

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # otp = models.CharField(max_length=9,   blank=True, null=True)

    phone = PhoneNumberField(unique=True)
    role = models.CharField(
        choices=[(e.value, e.value) for e in ROLES], max_length=32, editable=True
    )
    designation = models.CharField(max_length=100, default=None, choices=[(e.value, e.value) for e in DESIGNATION], null=True, blank=True)
    aadhar_no = models.CharField(max_length=12,blank=True,null=True)
    pan_no = models.CharField(max_length=10,blank=True,null=True)
    employee_id=models.CharField( max_length=50,unique=True,blank=True,null=True)
    employee_profile_photo=models.ImageField(upload_to='employee_profile_pic', null=True, blank=True)
    date_of_joining=models.DateField(blank=True,null=True)
    exclude_from_bt_date_logic = models.BooleanField(default=False)
    # status=models.BooleanField(default=True)z``
    email = models.EmailField(max_length=256, null=True, blank=True)
    entity_id = models.CharField(max_length=20,blank=True,null=True)

    state = models.CharField(max_length=100, blank=True,null=True)
    district = models.CharField(max_length=100,blank=True,null=True)
    city = models.CharField(max_length=100, blank=True,null=True)
    pincode = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{6}$', 'Pincode must be 6 digits')]
    )
    team = models.CharField(max_length=100, default=None, choices=[(e.value, e.value) for e in TEAM], null=True, blank=True)
    badge = models.CharField(max_length=100, blank=True,null=True)
    assign_so = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_so'
    )
    # Add these fields in User model
    phone_otp = models.CharField(max_length=6, null=True, blank=True)
    phone_otp_created_at = models.DateTimeField(null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)

    remember_username = models.CharField(max_length=256, null=True, blank=True)
    remember_password = models.CharField(max_length=256, null=True, blank=True)

    # manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["username", "role"]


    def phone_to_str(self):
        """Convert the type field to its string representation
        (the boneheaded way).
        """
        return str(self.phone)

    def __str__(self):
        # return str(self.username)
        return str(self.first_name) + " "+str(self.last_name)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    PasswordService().reset_password_email(token=reset_password_token.key,subject="Password change for Radian",email=reset_password_token.user.email)

class UserReward(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='rewards')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.phone} - ₹{self.amount} on {self.created_at.date()}"



class UserOtp(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    user_phone_unregistered = models.CharField(max_length=100, null=True, blank=True)
    # counter = models.IntegerField(default=0)
    otp_type=models.CharField(max_length=32, default=None, choices=[(e.value, e.value) for e in OTP_TYPE])
    user_otp_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    secret_key = models.TextField(max_length=32, default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


# def get_default_verification_token_expiry():
#     return datetime.now() + timedelta(minutes=5)


# TODO: delete unused or use update_or_created method
class VerificationToken(models.Model):
    verification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # identification can be phone/email/username/id_proof
    identification = models.CharField(max_length=256, null=True, blank=True)
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    expiry = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        self.expiry = timezone.localtime() + timedelta(minutes=5)
        super(VerificationToken, self).save(*args, **kwargs)


class UserDeviceDetails(models.Model):
    user_details_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(default="0.0.0.0")
    device_id = models.TextField()
    device_details = models.JSONField(default=dict)
    push_token = models.TextField()
    platform_type = models.CharField(
        max_length=32, default=None, choices=[(e.value, e.value) for e in PLATFORM_TYPE]
    )  # choices=['ios, android, web'])
    user_agent = models.TextField(blank=True, null=True)
    platform_version = models.CharField(max_length=128, blank=True, null=True)
    hardware_model = models.CharField(
        max_length=32, default=None, blank=True, null=True
    )
    software_version = models.CharField(max_length=32, default="1.0")
    locale_language = models.CharField(
        max_length=32, default=None, blank=True, null=True
    )
    imei = models.CharField(max_length=32, default=None, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    platform_device_id = models.CharField(
        max_length=32, default=None, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "device_id", "platform_type"],
                name="user_paltform_type_unique",
            ),
        ]


class Address(models.Model):
    address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    residential_ownership = models.CharField(
        max_length=255,
        choices=[(e.value, e.value) for e in RESENDITIAL_OWNERSHIP],
        default=RESENDITIAL_OWNERSHIP.INDIVIDUAL_OWNERSHIP.value,
        blank=True,
        null=True,
    )
    address_type = models.CharField(
        choices=[(e.value, e.value) for e in ADDRESS_TYPE],
        max_length=50,
        default=ADDRESS_TYPE.CORRESPONDENCE_ADDRESS.value,
    )
    account = models.ForeignKey(
        "account.Account", on_delete=models.CASCADE, related_name="user_addresse"
    )
    building_name = models.CharField(max_length=255, blank=True, null=True)

    street_name = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)

    state = models.CharField(max_length=255, blank=True, null=True)

    pincode = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

    latitude = models.DecimalField(
        max_digits=20, decimal_places=10, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=20, decimal_places=10, blank=True, null=True
    )

    def __str__(self) -> str:
        return str(self.address_id)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["address_type", "account"], name="ADDRESS_TYPE_ACCOUNT"
            ),
        ]


class TimeStamp(models.Model):
    timestamp_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    # TODO: remove blank=True, null=True
    status = models.CharField(
        choices=[(e.value, e.value) for e in TIMESTAMP],
        max_length=100,
        blank=True,
        null=True,
    )
    # check_out = models.DateTimeField(blank=True, null=True)
    # check_in = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    latitude = models.TextField()
    longitude = models.TextField()
    selfie = models.ImageField(upload_to=settings.SELFIE, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = "check_in"
