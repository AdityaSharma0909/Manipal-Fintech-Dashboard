from django.db import models
import uuid
from product.models import Product,WhiteGoods
from utils.constants import APPLICATION_STATUS, ApplicationType, REJECTION_APPLICATION
from users.models import User
from utils.constants import PurposeOfLoan
from account.models import Account, InsuranceProduct , NewAccount 
from lender.models import Lender
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.conf import settings
from utils.constants import LOAN_DOCUMENT,PERIOD,AMORTIZATIONTYPE,APPLICATION_OTP_TYPE,ASSET_DOCUMENT,LENDING_TYPE,APPROVED,REJECTED,ON_HOLD,DEVIATED,APPLICATION_DOCUMENT, NEW_APPLICATION_STATUS, VENDOR , FULFILMENT_TYPE
# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from branch.models import Branch
from simple_history.models import HistoricalRecords

# Create your models here.



class Application(models.Model):
    application_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account=models.ForeignKey(Account,on_delete=models.CASCADE,related_name="applications_account")
    status=models.CharField(choices=[(e.value, e.value) for e in APPLICATION_STATUS],max_length=100,default=APPLICATION_STATUS.NEW_APPLICATION.value)

    live_tracking_id=models.UUIDField(null=True, blank=True)
    branch=models.ForeignKey(Branch,on_delete=models.CASCADE,related_name="application_branch",blank=True,null=True)
    source_id=models.IntegerField(null=True, blank=True)
    application_number=models.CharField(max_length=15,unique=True)
    purpose_of_loan=models.CharField(choices=[(e.value, e.value) for e in PurposeOfLoan],max_length=300,null=True, blank=True)
    # eligible_amount=models.DecimalField(decimal_places=2,max_digits=20,blank=True,null=True)
    eligible_amount=models.IntegerField(null=True, blank=True)
    loan_amount=models.IntegerField(null=True, blank=True)
    contra_loan_amount=models.IntegerField(null=True, blank=True)
    contra_loan_processing_fee=models.FloatField(default=0)
    contra_loan_processing_fee_amount=models.IntegerField(default=0)
    contra_loan_gst_amount = models.IntegerField(default=0)
    contra_loan_stamp_duty_amount=models.IntegerField(default=0)
    contra_loan_net_payable_balance=models.IntegerField(default=0)
    product=models.ForeignKey(Product, on_delete=models.DO_NOTHING,related_name="application_product", null=True, blank=True)
    total_goods_price=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    # goods=models.ForeignKey(WhiteGoods, on_delete=models.CASCADE,related_name="white_goods_product",blank=True,null=True)
    total_weight=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    total_wastage=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    total_gross_weight=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    total_asset_price=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    net_weight=models.DecimalField(max_digits=10,decimal_places=2,null=True, blank=True)
    period=models.IntegerField(null=True, blank=True)
    application_type=models.CharField(max_length=100,default='NEW', choices=[(e.value,e.value) for e in ApplicationType])
    Originatedby=models.ForeignKey(User,on_delete=models.CASCADE,related_name="application_Originatedby",blank=True,null=True)
    appraisedBy= models.ForeignKey(User,on_delete=models.CASCADE,related_name="application_appraisedBy",blank=True,null=True)

    approvedByBM=models.ForeignKey(User,on_delete=models.CASCADE,related_name="application_approvedByBM",blank=True,null=True)
    source=models.CharField(max_length=100, default='RADIAN')
    approvedByBMAt=models.DateTimeField(auto_now_add=True,null=True, blank=True)
    approvedByCPC=models.ForeignKey(User,on_delete=models.CASCADE,related_name="application_approvedByCPC",blank=True,null=True)

    approvedByCPCAt=models.DateTimeField(auto_now_add=True,null=True, blank=True)
    bm_comment=models.TextField(null=True, blank=True)
    cpc_comment=models.TextField(null=True, blank=True)

    deviated_amount=models.IntegerField(null=True, blank=True)
    approvedByCM=models.ForeignKey(User,on_delete=models.CASCADE,related_name="application_approvedByCM",blank=True,null=True)
    approvalActionCM=models.CharField(choices=[(
        e, e) for e in [APPROVED,REJECTED,DEVIATED,ON_HOLD]], max_length=50,blank=True,null=True)
    cm_comment=models.TextField(null=True, blank=True)
    approvedByBH=models.ForeignKey(User,on_delete=models.CASCADE,related_name="application_approvedByBH",blank=True,null=True)
    approvalActionBH=models.CharField(choices=[(
        e, e) for e in [APPROVED,REJECTED,ON_HOLD]], max_length=50,blank=True,null=True)
    bh_comment=models.TextField(null=True, blank=True)
    
    processing_fee = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    
    current_gst_rate = models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True)
    gst=models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True)
    stamp_duty=models.IntegerField(blank=True,null=True)
    penalty=models.IntegerField(blank=True,null=True)
    ltv=models.IntegerField(blank=True,null=True)
    gold_rate_per_gram=models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True)
    lending_gold_rate_per_gram=models.DecimalField(max_digits=8,decimal_places=2,blank=True,null=True)
    tenure=models.IntegerField(blank=True,null=True)
    intrest_rate=models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    lender=models.ForeignKey(Lender,on_delete=models.CASCADE,related_name="application_lender",blank=True,null=True)
    disbursed_amount=models.IntegerField(null=True, blank=True)
    disbursed_date=models.DateTimeField(null=True, blank=True)
    due_date=models.DateTimeField(null=True, blank=True)
    processing_fee_percent = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(Decimal(0.0)), MaxValueValidator(Decimal(100.00))])
    penalty_percent = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(Decimal(0.0)), MaxValueValidator(Decimal(100.00))])
    # application.repayment_frequency = product.period
    repayment_frequency=models.CharField(choices=[(
        e.value, e.value) for e in PERIOD], max_length=50, default=PERIOD.MONTHLY.value)

    amortization_type = models.CharField(choices=[(
        e.value, e.value) for e in AMORTIZATIONTYPE], max_length=50, default=AMORTIZATIONTYPE.AMORTIZATION_SCHEDULE.value)
    #this amount will represent GL loan disbursal amount
    disbursal_amount = models.IntegerField(null=True, blank=True)
    # net payable balance incase o GL+PL loans this amount is total of both loan
    esign_signed_doc_link=models.CharField(max_length=1000, null=True, blank=True)
    esign_signature_link=models.CharField(max_length=1000, null=True, blank=True)
    esign_application_id=models.CharField(max_length=1000, null=True, blank=True)
    rejection_status = models.CharField(max_length=1000, null=True, blank=True)
    kick_back_comment=models.CharField(max_length=1000, null=True, blank=True)
    insurance_product = models.ForeignKey(InsuranceProduct,
                                          on_delete=models.DO_NOTHING,
                                          related_name='insurance_selected',
                                          null=True, blank=True)
    insurance_deducted=models.BooleanField(default=False)
    net_disbursed_amount=models.IntegerField(null=True, blank=True)
    insurance_amount_deducted=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    application_loan_type=models.CharField(choices=[(e.value, e.value) for e in LENDING_TYPE], max_length=50, default=LENDING_TYPE.GOLD_LOAN.value)
    requested_loan_amount=models.IntegerField(default=0)
    expected_income_increase=models.IntegerField(default=0)
    verify_the_usage=models.CharField(max_length=100, null=True, blank=True)
    co_remarks=models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)
    modefied_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    cibil_report_json=models.FileField(upload_to=settings.LOAN_DOCUMENT, null=True, blank=True)

    history=HistoricalRecords()
    def __str__(self):
        return str(self.application_id)

    def account_to_str(self):
        return str(self.account)
    
    def get_customer_firstname(self):
        return str(self.account.user.first_name)
    
    def get_customer_lastname(self):
        return str(self.account.user.last_name)



class AssetDocuments(models.Model):
    asset_document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_document_type = models.CharField(max_length=255,default="no_type", choices=ASSET_DOCUMENT, blank=True, null=True)
    asset=models.ForeignKey("asset.Asset",on_delete=models.CASCADE, blank=True, null=True,related_name="asset_document_asset")
    file_name = models.CharField(max_length=225, blank=True, null=True)
    file = models.FileField(max_length=225, blank=False, null=False, upload_to=settings.ASSET_DOCUMENT)
    # url = models.CharField(max_length=500, blank=True, null=True)
    application = models.ForeignKey(Application,on_delete=models.CASCADE,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, related_name='ASSET_DOC_USER', on_delete=models.CASCADE, null=True, blank=True)

 
    
    def get_file_url(self):
        return self.file.url
    
    def __str__(self):
        return str(self.asset_document_id)



@receiver(pre_delete, sender=AssetDocuments)
def asset_documents_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)


   
class LoanDocument(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=255,default="no_type", choices=LOAN_DOCUMENT, blank=True, null=True)
    file_name = models.CharField(max_length=225, blank=True, null=True)
    file = models.FileField(max_length=225,blank=False, null=False, upload_to=settings.LOAN_DOCUMENT)
    # url = models.CharField(max_length=500, blank=True, null=True)
    application = models.ForeignKey(Application,on_delete=models.CASCADE,blank=True,null=True, related_name="loan_document_application")
    esign_id=models.CharField(max_length=1000, null=True, blank=True,unique=True)
    esign_signature_link=models.CharField(max_length=1000, null=True, blank=True)
    esign_signed_doc_link=models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


   # TODO e-sign:
    # signed_doc_link
    # esign_signature_link
    # esign_id =  charfield, unique=True


    def get_file_url(self):
        return self.file.url
    
    def __str__(self):
        return str(self.document_id)
    

@receiver(pre_delete, sender=LoanDocument)
def loan_document_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)

class ApplicationDocument(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=255,default="no_type", choices=APPLICATION_DOCUMENT, blank=True, null=True)
    file_name = models.CharField(max_length=225, blank=True, null=True)
    file = models.FileField(max_length=225,blank=False, null=False, upload_to=settings.APPLICATION_DOCUMENT)
    # url = models.CharField(max_length=500, blank=True, null=True)
    application = models.ForeignKey(Application,on_delete=models.CASCADE,blank=True,null=True, related_name="application_document")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, related_name='APPLICATION_DOC_USER', on_delete=models.CASCADE, null=True, blank=True)

    def get_file_url(self):
        return self.file.url
    
    def __str__(self):
        return str(self.document_id)
    

@receiver(pre_delete, sender=ApplicationDocument)
def application_document_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
   

class ApplicationGoodsMapping(models.Model):
    application_goods_mapping_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    application = models.ForeignKey(Application, on_delete=models.CASCADE,related_name="agmMap_application")
    goods = models.ForeignKey(WhiteGoods, on_delete=models.CASCADE,related_name="agmMap_goods")
    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)
    modefied_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return str(self.application_goods_mapping_id)
 

# from users.models import User
from django.conf import settings

class ApplicationOtp(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    otp_type=models.CharField(max_length=32, default=None, choices=[(e.value, e.value) for e in APPLICATION_OTP_TYPE])
    secret_key = models.TextField(max_length=32, default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    # class Meta:
    #     constraints = [UniqueConstraint(fields=['account_number', "ifsc",'account'],
    #                                     name='unique_application_otp')]



class NewApplication(models.Model):
    new_application_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account=models.ForeignKey(NewAccount,on_delete=models.CASCADE,related_name="new_applications_account", blank=True, null=True)
    onboarding_application = models.ForeignKey(
        "onboarding_v2.ApplicationV2",
        on_delete=models.CASCADE,
        related_name="new_applications",
        blank=True,
        null=True,
    )
    status=models.CharField(choices=[(e.value, e.value) for e in NEW_APPLICATION_STATUS],max_length=100)
    application_number=models.CharField(max_length=15,unique=True)
    vendor = models.CharField(choices=[(e.value, e.value) for e in VENDOR],max_length=100) 
    fulfilment_type = models.CharField(choices=[(e.value, e.value) for e in FULFILMENT_TYPE],max_length=100)
    application_reference_number=models.CharField(max_length=100, null=True, blank=True)
    ddp_reference_number=models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(User, blank=True, null= True, on_delete=models.CASCADE, related_name="new_application_created_by",)
    modified_by = models.ForeignKey(User, blank=True, null= True, on_delete=models.CASCADE, related_name="new_application_modified_by",)
    created_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)
    modefied_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return str(self.new_application_id)
