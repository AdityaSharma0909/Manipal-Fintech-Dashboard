from django.db import models
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
import uuid
from users.models import User
from django.conf import settings
from product.models import Product
from django.db.models import UniqueConstraint
from utils.envSetup import environment

from utils.constants import RADIAN_OFFICE_IN_INDIA


# Create your models here.
class Branch(models.Model):
    branch_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    branch_code = models.CharField(max_length=255)
    email = models.EmailField(default=environment.DEFAULT_CPC_ADMIN_EMAIL)
    address = models.CharField(max_length=255)
    opening_date=models.DateField(blank=True, null=True)
    assistant_bm=models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name="abm")
    cluster_manager=models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name="cluster")
    regional_head=models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name="region")
    branch_manager=models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name="bm")
    state=models.CharField(max_length=100,blank=True,null=True, choices=[(i,i) for i in RADIAN_OFFICE_IN_INDIA])
    branch_name=models.CharField(max_length=100,blank=True,null=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    # stamp_duty_percent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # stamp_duty_amount = models.IntegerField(blank=True, null=True)
    # stamp_duty_minimum_amount_eligibility = models.IntegerField(blank=True, null=True)
    phone = PhoneNumberField()
    
    def __str__(self):
        return f"{self.branch_name} ({self.branch_code})"

class StampDutyCharges(models.Model):
    stamp_duty_charge_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(Branch, related_name='branch_stamp_duty', on_delete=models.CASCADE)

    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stamp_duty_percent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stamp_duty_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def clean(self, *args, **kwargs):
        if (self.stamp_duty_percent is None) == (self.stamp_duty_amount is None):
            raise ValidationError('stamp_duty_percent or stamp_duty_amount, only anyone is allowed')
        if (self.minimum_amount is None) and (self.maximum_amount is None):
            raise ValidationError('minimum_amount or maximum_amount anyone is required')
        return super().clean(*args, **kwargs)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                name="minimum_amount_gte_maximum_amount",
                check=models.Q(minimum_amount__lte=models.F("maximum_amount")),
            ),
        ]

class BranchUserMapping(models.Model):
    branch_user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    branch = models.ForeignKey(Branch, related_name='branch_lm_map', on_delete=models.CASCADE, blank=False, null=False)
    user = models.ForeignKey(User, related_name='lm_branch_map', on_delete=models.CASCADE)
    source_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'branch'],
                                        name='user_branch_unique'), ]

    def __str__(self):
        return f"{self.branch.branch_name} [{self.user.first_name}] ({self.branch_user_id})"


class BranchProductMapping(models.Model):
    branch_product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    branch = models.ForeignKey(Branch, related_name='branch_product_map', on_delete=models.CASCADE, blank=False, null=False)
    product = models.ForeignKey(Product, related_name='product_branch_map', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [UniqueConstraint(fields=['branch', 'product'],
                                        name='branch_product_unique'), ]
    