from django.db import models
from account.models import Account
from application.models import Application
from utils.constants import PurposeOfLoan, ACCOMODATION, ADDRESS_LOCATING_DIFFICULTY, AREA_SQFT , PHOTO_TYPE
from product.models import Product
from django.core.validators import MaxValueValidator, MinValueValidator

import uuid
from lender.models import Lender
from branch.models import Branch
from users.models import User
from utils.constants import LOAN_STATUS
from simple_history.models import HistoricalRecords

# Create your models here.
class Loan(models.Model):
    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    loan_number = models.CharField(max_length=18, unique=True)
    application = models.ForeignKey(Application, on_delete=models.DO_NOTHING, related_name="loan_application")
    status = models.CharField(choices=[(e.value, e.value) for e in LOAN_STATUS], max_length=100,
                              default=LOAN_STATUS.NEW.value)
    term = models.CharField(max_length=255)
    intrest_rate = models.DecimalField(max_digits=10, decimal_places=2)
    bm_comment = models.TextField(null=True, blank=True)
    cpc_comment = models.TextField(null=True, blank=True)
    processing_fee = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    stamp_duty = models.IntegerField(blank=True, null=True)
    penalty = models.IntegerField(blank=True, null=True)
    ltv = models.IntegerField(blank=True, null=True)
    tenure = models.IntegerField(blank=True, null=True)
    lender = models.ForeignKey(Lender, on_delete=models.CASCADE, related_name="loan_lender", blank=True, null=True)
    loan_amount = models.IntegerField()
    loan_type = models.CharField(max_length=255)
    days_past_dues = models.IntegerField()
    current_amount = models.DecimalField(decimal_places=2, max_digits=15)
    purpose_of_loan = models.CharField(choices=[(e.value, e.value) for e in PurposeOfLoan], max_length=300,
                                       null=True, blank=True)
    eligible_amount = models.IntegerField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name="loan_product", blank=True,
                                null=True)
    total_goods_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # goods=models.ForeignKey(WhiteGoods, on_delete=models.CASCADE,related_name="white_goods_product",blank=True,null=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    period = models.IntegerField(null=True, blank=True)
    Originatedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loan_Originatedby", blank=True,
                                     null=True)
    
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, related_name="loan_branch", blank=True,
                                     null=True)
    
    appraisedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loan_appraisedBy", blank=True,
                                    null=True)
    approvedByBM = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loan_approvedByBM", blank=True,
                                     null=True)
    approvedByBMAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    approvedByCPC = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loan_approvedByCPC", blank=True,
                                      null=True)
    approvedByCPCAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    current_gst_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    gst = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    gold_rate_per_gram = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    lending_gold_rate_per_gram = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    disbursed_amount = models.IntegerField(null=True, blank=True)
    disbursed_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    disbursal_amount = models.IntegerField(null=True, blank=True)
    # net payable balance
    net_disbursed_amount = models.IntegerField(null=True, blank=True)
    last_payment_date = models.DateField(null=True, blank=True)
    current_emi = models.FloatField(null=True, blank=True)
    interest_accrued_till_date = models.FloatField(null=True, blank=True)
    principal_paid = models.FloatField(default=0)
    interest_paid = models.FloatField(default=0)
    penalty_paid = models.FloatField(default=0)
    principal_remaining = models.FloatField(null=True, blank=True)
    interest_remaining = models.FloatField(null=True, blank=True)
    next_due_date=models.DateField(null=True, blank=True)
    next_due_generation_date=models.DateField(null=True, blank=True)
    accrual_on_hold=models.BooleanField(default=False)
    interest_last_accrued_on=models.DateField(null=True, blank=True)
    modified_at=models.DateTimeField(auto_now_add=True,null=True, blank=True)
    history=HistoricalRecords()

    # TODO: add timestamp

    def __str__(self):
        return self.loan_number
    
    def get_customer_firstname(self):
        return str(self.application.account.user.first_name)
    
    def get_customer_lastname(self):
        return str(self.application.account.user.last_name)
    
    def get_customer_account_id(self):
        return str(self.application.account.account_id)
    
    def get_customer_customer_id(self):
        return str(self.application.account.customer_id)
    
    def get_customer_email(self):
        return str(self.application.account.email)
    
    def get_customer_occupation(self):
        return str(self.application.account.occupation)
    
    def get_customer_sub_occupation(self):
        return str(self.application.account.sub_occupation)
    
    def get_customer_net_annual_income(self):
        return str(self.application.account.net_annual_income)
    
    def get_customer_aadhar_no(self):
        return str(self.application.account.aadhar_no)
    
    def get_customer_pan_no(self):
        return str(self.application.account.pan_no)
    



class LoanEMISchedule(models.Model):
    loan_emi_header_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    principal = models.IntegerField()
    emi_amount = models.IntegerField()
    data=models.JSONField(null=True, blank=True)


class LoanEMIRecord(models.Model):
    loan_emi_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    loan_emi_header = models.ForeignKey(LoanEMISchedule, on_delete=models.CASCADE,related_name='loan_emi_schedule')
    created_at = models.DateTimeField(auto_now_add=True)
    sequence_no = models.IntegerField()
    amount = models.IntegerField()
    emi_amount = models.IntegerField()
    interest = models.IntegerField()
    principal = models.IntegerField()
    bill_generation_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    paid = models.BooleanField(default=False)


class LiveTracking(models.Model):
    track_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="livetracking_loan")
    loan_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name="livetracking_loanmanager")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="livetracking_customer")

    # Log file will be maintained on S3 or any server to store track data 
    # From Redis track data will be moved to media storage server as csv file 
    track_file = models.CharField(max_length=1024, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class LoanPaymentTransaction(models.Model):
    loan_payment_transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="loan_payment_transaction")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    payment_mode = models.CharField(max_length=100, null=True, blank=True)
    payment_amount = models.FloatField(default=0)
    payment_date = models.DateField(null=True, blank=True)
    received_by = models.CharField(max_length=100, null=True, blank=True)
    interest=models.FloatField(default=0)
    principal=models.FloatField(default=0)
    penalty=models.FloatField(default=0)
    is_cleared = models.BooleanField(default=False)


class LoanTakeOver(models.Model):
    take_over_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    lender_name = models.CharField(max_length=100)
    gold_weight_pledged = models.CharField(max_length=100)
    karat=models.IntegerField(validators=[MaxValueValidator(22),MinValueValidator(18)], null=True, blank=True)
    loan_amount = models.FloatField()
    interest_rate = models.FloatField()
    tenure = models.IntegerField()
    # total_payment_done = models.FloatField()
    requested_amount_from_radian = models.FloatField()
    # loan_amount_remaining = models.FloatField()
    total_release_amount = models.FloatField()
    loan_start_date = models.DateField()
    maturity_date = models.DateField()
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='loan_take_over_app')
    lender=models.ForeignKey(Lender, on_delete=models.CASCADE, related_name='take_over_loan_lender', null=True, blank=True)
    loan_reference_number = models.CharField(max_length=100)

class DemandGeneration(models.Model):
    loan=models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='loan_bill_generation')
    emi_record=models.OneToOneField(LoanEMIRecord, on_delete=models.CASCADE, related_name='loan_bill_emi_record',
                                 null=True, blank=True, unique=True)
    total_amount=models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    total_principal=models.DecimalField(null=True, blank=True,decimal_places=2, max_digits=10)
    total_interest=models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    total_penalty=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    principal_remaining=models.DecimalField(null=True, blank=True,decimal_places=2, max_digits=10)
    interest_remaining=models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    penalty_remaining=models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    total_amount_paid=models.DecimalField(null=True, blank=True,decimal_places=2, max_digits=10)
    principal_paid=models.DecimalField(null=True, blank=True,decimal_places=2, max_digits=10)
    interest_paid=models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    penalty_paid=models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    bill_paid=models.BooleanField(default=False)


class OtherLenderApprainsal(models.Model):
    appraisal_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    loan=models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='other_lender_appraisal', unique=True)
    loan_amount=models.IntegerField()
    loan_number=models.CharField(max_length=64)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="other_lender_appraisal_created_by")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class TakeOverResidenceAddress(models.Model):
    take_over_residence_details_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    account=models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_take_over_residence_details')
    prospect_no=models.CharField(max_length=100, null=True, blank=True)
    person_met=models.CharField(max_length=100, null=True, blank=True)
    relationship_with_applicant=models.CharField(max_length=100, null=True, blank=True)
    any_other_earning_family_member=models.CharField(max_length=100, null=True, blank=True)
    family_member_employement_details=models.CharField(max_length=100, null=True, blank=True)
    no_years_at_residence=models.CharField(max_length=100, null=True, blank=True)
    locating_address_difficulty=models.CharField(max_length=100, choices=[(e.value, e.value) for e in ADDRESS_LOCATING_DIFFICULTY], null=True, blank=True)
    type_of_accomodation=models.CharField(max_length=100, choices=[(e.value, e.value) for e in ACCOMODATION], null=True, blank=True)
    area_sqft=models.CharField(max_length=100, choices=[(e.value, e.value ) for e in AREA_SQFT], null=True, blank=True)
    neighbor_check=models.BooleanField(default=False)
    is_feedback_positive=models.BooleanField(default=False)
    no_adults=models.IntegerField(default=0)
    no_children=models.IntegerField(default=0)


class GprsPhotos(models.Model):
    gprs_photos_id=models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    account=models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_gprs_photos', null=True, blank=True)
    application=models.ForeignKey(Application, on_delete=models.CASCADE, related_name='application_gprs_photos', null=True, blank=True)
    take_over_residence=models.ForeignKey(TakeOverResidenceAddress, on_delete=models.CASCADE, related_name='gprs_photos',null=True, blank=True)
    photo_type=models.CharField(max_length=100, choices=[(e.value, e.value) for e in PHOTO_TYPE], null=True, blank=True)
    gprs_photos = models.FileField(upload_to='bt_gprs_photos', null=True, blank=True)
    satellite_map_photos = models.FileField(upload_to='bt_gprs_satellite_photos', null=True, blank=True)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    address_details = models.CharField(max_length=1000, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)


