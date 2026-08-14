from django.db import models

# Create your models here.
from django.db import models
import uuid
from account.models import Account
from utils.constants import  NATURE_OF_BUSINESS, RESIDENTIAL_NO_OF_YEARS, RELATION ,RESIDENTIAL_OWNERSHIP
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField


User=get_user_model()

# Create your models here.
class Reference_PD(models.Model):
    pd_details_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    account = models.ForeignKey(Account ,on_delete=models.CASCADE ,related_name="refenrence_pd_account")
    enterprise_name = models.CharField(max_length=128, null=False, blank=False)
    nature_of_business = models.CharField(choices=[(e.value, e.value) for e in NATURE_OF_BUSINESS],max_length=20)
    sub_nature_of_business = models.CharField(max_length=32, null=False, blank=False)
    residential = models.CharField(choices=[(e.value, e.value) for e in RESIDENTIAL_OWNERSHIP],max_length=20)
    number_of_years = models.CharField(choices=[(e.value, e.value) for e in RESIDENTIAL_NO_OF_YEARS],max_length=20)
    number_of_family_members = models.IntegerField(null=False)
    number_of_earning_members = models.IntegerField(null=False)
    phone = PhoneNumberField()
    relation_with_applicant = models.CharField(choices=[(e.value, e.value) for e in RELATION],max_length=50)
    others_relations = models.CharField(max_length=50, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True )
    modefied_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return str(self.pd_details_id)

    