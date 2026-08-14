from django.db import models
import uuid
from utils.constants import HOUSE_OWNERSHIP , SHOP_OWNERSHIP , NO_OF_YEARS , NATURE_OF_BUSINESS , YES_OR_NO
from account.models import Account
# Create your models here.

class CreditStatus(models.Model):
    credit_status_id = models.UUIDField(primary_key=True , default=uuid.uuid4, editable=False,unique=True)
    account = models.ForeignKey(Account ,on_delete=models.CASCADE ,related_name="creditstatus_account")
    house_ownership = models.CharField(choices=[(e.value , e.value) for e in HOUSE_OWNERSHIP], max_length=20)
    house_number_of_year = models.CharField(choices=[(e.value , e.value) for e in NO_OF_YEARS], max_length=20)
    shop_ownership = models.CharField(choices=[(e.value , e.value) for e in SHOP_OWNERSHIP], max_length=20)
    shop_number_of_year = models.CharField(choices=[(e.value , e.value) for e in NO_OF_YEARS], max_length=20)
    nature_of_business = models.CharField(choices=[(e.value , e.value) for e in NATURE_OF_BUSINESS], max_length=20) 
    nob_others = models.CharField(max_length=500, blank=True, null=True)
    monthly_income = models.IntegerField()
    monthly_expenditure = models.IntegerField()
    no_of_loans_running = models.IntegerField()
    no_of_loans_closed_in_last_1_year = models.IntegerField()
    any_loan_applied_in_last_30_days = models.CharField(choices=[(e.value , e.value) for e in YES_OR_NO], max_length=20)
    account_held_for_no_of_years = models.IntegerField()
    fixed_assets_held_by_him_and_family = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True) 

    def __str__(self):
        return str(self.credit_status_id)

    