from django.db import models
import uuid
from utils.constants import LOAN_TYPE ,PRODUCT_TYPE , INSURANCE_APPLICABLE
from django.contrib.auth import get_user_model
from lender.models import Lender
from utils.constants import PERIOD,AMORTIZATIONTYPE
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal



User=get_user_model()
# Create your models here.


class Product(models.Model):
    product_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product_number = models.CharField(max_length=10)
    product_type = models.CharField(choices=[(
        e.value, e.value) for e in LOAN_TYPE], max_length=50, default=LOAN_TYPE.GOLD_LOAN.value)
    product_name = models.CharField(max_length=255)
    # pinnace = models.CharField(max_length=255, blank=True, null=True)
    product_category=models.CharField(choices=[(
        e.value, e.value) for e in PRODUCT_TYPE], max_length=50, null =True,blank=True)
    # minimum_gold=models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    pre_payment_col=models.PositiveIntegerField(default=0)
    processing_fee = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    
    penalty = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(Decimal(0.0)), MaxValueValidator(Decimal(100.00))])
    has_white_goods=models.BooleanField(default=False,blank=True,null=True)
    period=models.CharField(choices=[(
        e.value, e.value) for e in PERIOD], max_length=50, default=PERIOD.MONTHLY.value)
    has_required_documents=models.BooleanField(default=False,blank=True,null=True)
    maximum_ticket_size = models.IntegerField(
        blank=True, null=True)
    minimum_ticket_size = models.IntegerField(
        blank=True, null=True)
    lender = models.ForeignKey(Lender,on_delete=models.CASCADE,related_name="product_lender")
    ltv_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tenure = models.IntegerField()
    other_deduction = models.JSONField(null=True, blank=True)
    # intrest_rate = models.IntegerField(default=0)
    interest_rate = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    amortization_type = models.CharField(choices=[(
        e.value, e.value) for e in AMORTIZATIONTYPE], max_length=50, default=AMORTIZATIONTYPE.AMORTIZATION_SCHEDULE.value)
    contra_product = models.ForeignKey("self",on_delete=models.CASCADE,related_name="related_product",null=True,blank=True)
    is_insurance_applicable = models.BooleanField(default=True,blank=True,null=True)
    insurance_applicable_on = models.CharField(choices=[(
        e.value, e.value) for e in INSURANCE_APPLICABLE], max_length=50, default=INSURANCE_APPLICABLE.ACCOUNT.value)
    is_stamp_duty_applicable = models.BooleanField(default=True,blank=True,null=True)
    available_in_branches = models.ManyToManyField(
        'branch.Branch', blank=True, related_name='available_products_in_branch')
    is_available_to_all_branches = models.BooleanField(default=True)
    active=models.BooleanField(default=True)
    def __str__(self) :
        return str(self.product_number)
    

class WhiteGoods(models.Model):
     goods_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    #  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_white_goods")
     goods_name = models.CharField(max_length=255)
     goods_description = models.CharField(max_length=255)
     goods_price = models.IntegerField(default=0)
     minimum_order_quantity = models.IntegerField(default=0)
     quantity_available=models.IntegerField(default=0)
     available_in=models.JSONField(default=dict)
    #  quantity = models.IntegerField(default=0,blank=True,null=True)
     created_At = models.DateTimeField(auto_now_add=True)
     modified_At = models.DateTimeField(auto_now=True)
     created_by=models.ForeignKey(
         User, on_delete=models.CASCADE, related_name="white_goods_created_by")

     
     def __str__(self) :
         return str(self.goods_name)
     

class ProductSpecificDocuments(models.Model):
     product_document_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_specific_documents")
     document_name = models.CharField(max_length=255)
     document_description = models.CharField(max_length=255)
     document_type = models.CharField(max_length=255) # Bank_statement & Land document
     is_required = models.BooleanField(default=True)
     created_At = models.DateTimeField(auto_now_add=True)
     modified_At = models.DateTimeField(auto_now=True)
     created_by=models.ForeignKey(
         User, on_delete=models.CASCADE, related_name="product_specific_documents_created_by")
     def __str__(self) :
         return str(self.document_name)
     
class ProductWhiteGoodsMapping(models.Model):
     product_white_goods_mapping_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True)
     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_white_goods_mapping")
     
     goods = models.ForeignKey(WhiteGoods, on_delete=models.CASCADE, related_name="product_white_goods_mapping")
     created_At = models.DateTimeField(auto_now_add=True)
     modified_At = models.DateTimeField(auto_now=True)
     created_by=models.ForeignKey(
         User, on_delete=models.CASCADE, related_name="product_white_goods_mapping_created_by")

     

