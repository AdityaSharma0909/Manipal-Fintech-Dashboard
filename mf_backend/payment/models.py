from django.db import models
import uuid
from utils.constants import LOAN_TYPE ,PRODUCT_TYPE
from django.contrib.auth import get_user_model
from lender.models import Lender
from utils.constants import DOCUMENT_TYPE,PERIOD,AMORTIZATIONTYPE
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# from user.models import User
from loan.models import Loan

from utils.constants import REPAYMENT_PAYMENT_STATUS, REPAYMENT_PAYMENT_MODE

from application.models import Application
from django.db import transaction
from django.db.models import Max
from utils.constants import SALES_PAYOUT_TYPE


User=get_user_model()

# Create your models here.
class Repayment(models.Model):
    repayment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="repayment_loan")
    initiated_by=models.ForeignKey(User, on_delete=models.CASCADE, related_name="repayment_initiated_by") 

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(Decimal(0.0))])
    reference_id = models.CharField(max_length=32, unique=True) # our generated ref_id
    payment_mode = models.CharField(choices=[(e.value, e.value) for e in REPAYMENT_PAYMENT_MODE], max_length=16) #transaction_type
    payment_status = models.CharField(choices=[(e.value, e.value) for e in REPAYMENT_PAYMENT_STATUS], max_length=32, default=REPAYMENT_PAYMENT_STATUS.TRANSACTION_UNDER_PROCESS_2.value)
    remarks = models.CharField(max_length=64)

    utr_no = models.CharField(max_length=16, null=True, blank=True)
    txn_id = models.CharField(max_length=32, null=True, blank=True)
    upi_ref_id = models.CharField(max_length=128, null=True, blank=True)

    sender_vpa = models.CharField(max_length=32, null=True, blank=True)
    sender_name = models.CharField(max_length=128, null=True, blank=True)
    receiver_vpa = models.CharField(max_length=32)
    receiver_name = models.CharField(max_length=128, null=True, blank=True)
    receiver_account_number = models.CharField(max_length=16, null=True, blank=True) # "999131213212"
    
    created_At = models.DateTimeField(auto_now_add=True)
    modified_At = models.DateTimeField(auto_now=True)
    created_by=models.ForeignKey(User, on_delete=models.CASCADE, related_name="repayment_created_by")
    modified_by=models.ForeignKey(User, on_delete=models.CASCADE, related_name="repayment_modified_by")


    def get_payment_status(self, status: int) -> str :
        if status == 0:
            return REPAYMENT_PAYMENT_STATUS.TRANSACTION_FAILED_0.value
        elif status == 1:
            return REPAYMENT_PAYMENT_STATUS.TRANSACTION_SUCCESSFUL_1.value
        if status == 2:
            return REPAYMENT_PAYMENT_STATUS.TRANSACTION_UNDER_PROCESS_2.value
        if status == 3:
            return REPAYMENT_PAYMENT_STATUS.TRANSACTION_UNDER_PROCESS_3.value
        if status == 4:
            return REPAYMENT_PAYMENT_STATUS.TRANSACTION_UNDER_PROCESS_4.value


class BharatSwasthyaRepayment(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="bs_repayments")
    initiated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bs_repayment_initiated_by")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=20, unique=True)
    pg_ref_num = models.CharField(max_length=50, null=True, blank=True)
    pg_txn_message = models.TextField(null=True, blank=True)
    rrn = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    txn_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bs_repayment_created_by")

    @transaction.atomic
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()

        super().save(*args, **kwargs)

    def generate_order_id(self):
        last_order = BharatSwasthyaRepayment.objects.aggregate(Max('order_id'))['order_id__max']

        if last_order:
            new_order_id = str(int(last_order) + 1).zfill(6)
        else:
            new_order_id = '000001'

        return new_order_id


class SalesOfficerPayout(models.Model):
    payout_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    so_user = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True, related_name="so_payouts")
    payout_type = models.CharField(choices=[(e.value, e.value) for e in SALES_PAYOUT_TYPE], max_length=16)
    loan_id = models.CharField(max_length=64, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    customer_id = models.CharField(max_length=64, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    lead_id = models.CharField(max_length=64, null=True, blank=True)
    agent_name = models.CharField(max_length=255, null=True, blank=True)
    agent_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="agent_payouts")
    agent_type = models.CharField(max_length=32, null=True, blank=True)
    request_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    disbursed_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    disbursed_on = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    utr = models.CharField(max_length=64, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    clawback_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0)
    settled_on = models.DateTimeField(null=True, blank=True)
    settlement_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="so_payouts_created")
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="so_payouts_modified")

    def __str__(self):
        return f"{self.payout_type} - {self.so_user.phone} - ₹{self.amount}"
