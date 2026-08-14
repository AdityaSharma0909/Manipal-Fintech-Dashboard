from django.db import models
import uuid

from disbursements.service.constants import DisbursalConstants
from loan.models import Loan
from application.models import Application
from account.models import Account
from users.models import User
from utils.constants import PAYMENT_STATUS


# Create your models here.

class Disbursement(models.Model):
    disbursement_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    loan=models.ForeignKey(Loan,on_delete=models.CASCADE, related_name='loan_disbursement_transactions', null=True,blank=True)
    application=models.ForeignKey(Application,on_delete=models.CASCADE,blank=True,null=True,related_name='loan_disbursed_applications')
    disbursement_amount=models.DecimalField(max_digits=15,decimal_places=2)
    disbursal_date=models.DateField(null=True)
    disbursement_status=models.CharField(choices=[(e.value,e.value) for e in DisbursalConstants], max_length=100)
    payment_mode = models.CharField(max_length=25, null=True, blank=True)
    utr_no=models.CharField(unique=True,max_length=50,null=True, blank=True)
    created_by=models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True, related_name='loan_disbursed_by')
    created_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    payment_status=models.IntegerField(default=0, choices=[(e.value, e.value) for e in PAYMENT_STATUS])
    

    