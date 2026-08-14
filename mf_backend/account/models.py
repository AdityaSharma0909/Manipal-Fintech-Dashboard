from django.db import models

from branch.models import Branch
from lender.models import Lender
from users.models import User
from product.models import Product
import uuid
from utils.constants import GENDER,OCCUPATION,SUB_OCCUPATION,ACCOUNT_STATUS,RELIGION,CASTE,EDUCATION,MARRIED_STATUS,RELATION,ACCOUNT_TYPE, ACCOUNT_PURPOSE , LENDING_TYPE , APPLICANT_TYPE , ROLES, AGENT_ACCOUNT_STATUS, AGENT_EDUCATION , AGENT_OCCUPATION, LEAD_DOCUMENT_TYPE, NEW_ACCOUNT_STATUS, NEW_LEAD_SOURCE
from phonenumber_field.modelfields import PhoneNumberField
from document.models import Document
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from django.conf import settings



def validate_pan_card(value):
    if len(value)==10:
        return value
    else:
        raise ValidationError("Length of Pancard number should be equal to 10")
 

    
class Account(models.Model):
    
    account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    # title=models.CharField(choices=[(e.value, e.value) for e in TITLE],max_length=8)
    customer_id=models.CharField(max_length=12,unique=True)
    # first_name=models.CharField(max_length=255 ,blank=True, null=True)
    # last_name=models.CharField(max_length=255 ,blank=True, null=True)
    email = models.EmailField(blank=True,null=True)
    # mobile_number = PhoneNumberField(unique=True)
    gender = models.CharField(choices=[(e.value, e.value) for e in GENDER],max_length=20)
    year_of_birth = models.DateTimeField()
    occupation=models.CharField(choices=[(e.value, e.value) for e in OCCUPATION],max_length=100,default=OCCUPATION.OTHERS.value)
    sub_occupation=models.CharField(choices=[(e.value, e.value) for e in SUB_OCCUPATION],max_length=100,default=SUB_OCCUPATION.OTHER.value)
    profile_photo = models.ForeignKey(Document, related_name='profile_photo_doc', on_delete=models.CASCADE, null=True, blank=True)
    net_annual_income =models.IntegerField()
    aadhar_no =models.CharField(max_length=100, null=True, blank=True)
    aadhar_meta_field=models.JSONField(null=True, blank=True)
    pan_no =models.CharField(null=True, blank=True, max_length=20, validators=[validate_pan_card], unique=True)
    pan_verified=models.BooleanField(default=False)
    aadhar_verified=models.BooleanField(default=False)
    mother_name=models.CharField(max_length=255)
    father_name=models.CharField(max_length=255)
    spouse_name=models.CharField(max_length=255,blank=True,null=True)
    education=models.CharField(choices=[(e.value, e.value) for e in EDUCATION],max_length=100,default=EDUCATION.OTHERS.value,blank=True,null=True)
    religion=models.CharField(choices=[(e.value, e.value) for e in RELIGION],max_length=100,default=RELIGION.OTHER.value)
    disablity=models.BooleanField(default=False,blank=True,null=True)
    nationality=models.CharField(max_length=255,default="INDIA",blank=True,null=True)
    caste=models.CharField(choices=[(e.value, e.value) for e in CASTE],max_length=100,default=CASTE.OTHERS.value,blank=True,null=True)
    maritial_status=models.CharField(choices=[(e.value, e.value) for e in MARRIED_STATUS],max_length=100,blank=True,null=True)
    status=models.CharField(choices=[(e.value, e.value) for e in ACCOUNT_STATUS],max_length=100,default=ACCOUNT_STATUS.NEW_ACCOUNT_CREATED.value,blank=True,null=True)
    # profile_image=models.ImageField(default='default.png', upload_to='profile_pics')
    user = models.ForeignKey(
     User, on_delete=models.CASCADE, related_name="account_user", default=None
       )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
 
    created_at = models.DateTimeField(auto_now_add=True )
    modefied_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    insurance_product = models.ForeignKey('account.InsuranceProduct',
                                          on_delete=models.DO_NOTHING,
                                          related_name='insurance_product_chosen',
                                          null=True, blank=True)
    branch=models.ForeignKey(Branch, on_delete=models.PROTECT,related_name='account_branch',
                             null=True, blank=True)
    pan_meta_field = models.JSONField(null=True, blank=True)
    insurance_amount=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_amount_covered_from = models.ForeignKey('application.Application',
                                                      on_delete=models.DO_NOTHING,
                                                      related_name='insurance_deducted_from',
                                                      null=True,
                                                      blank=True ) # set it when loan is disbursed
    history=HistoricalRecords()
    applicant_type=models.CharField(choices=[(e.value, e.value) for e in APPLICANT_TYPE],max_length=100,default=APPLICANT_TYPE.APPLICANT.value)
    applicant=models.ForeignKey(
     User, on_delete=models.CASCADE, related_name="account_applicant", null=True, blank=True
       )


    def __str__(self): 
        return str(self.account_id )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.branch and self.created_by:
            branch_mapping = self.created_by.lm_branch_map.first()
            if branch_mapping:
                self.branch = branch_mapping.branch
        super(Account, self).save(force_insert, force_update, using, update_fields)




    def get_customer_firstname(self):
        return str(self.user.first_name)
    
    def get_customer_lastname(self):
        return str(self.user.last_name)


class InsuranceProduct(models.Model):
    insurance_policy_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='insurance_product_product',null=True , blank=True)
    product_name=models.CharField(max_length=100)
    company_name=models.CharField(max_length=100)
    company=models.ForeignKey(Lender, on_delete=models.CASCADE, related_name='insurance_lender', null=True, blank=True)
    validity=models.IntegerField(verbose_name='validity in months')
    coverage=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10, decimal_places=2 , null=True , blank=True)
    insurance_benefits=models.CharField(max_length=1000 , null=True , blank=True)
    policy_meta=models.JSONField(null=True, blank=True)
    insurance_policy_type = models.CharField(choices=[(e.value, e.value) for e in LENDING_TYPE],max_length=100,default=LENDING_TYPE.GOLD_LOAN.value,blank=True,null=True)
    tenure = models.IntegerField(null=True , blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2 ,null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)

class BankAccount(models.Model):
    bank_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account ,on_delete=models.CASCADE ,related_name="bankaccount_account")
    verified = models.BooleanField(default=False)
    account_number = models.CharField(max_length=100)
    ifsc =models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=255)
    account_purpose = models.CharField(choices=[(e.value, e.value) for e in ACCOUNT_PURPOSE],max_length=20, default=ACCOUNT_PURPOSE.LOAN_DISBURSEMENT.value)
    account_type = models.CharField(choices=[(e.value, e.value) for e in ACCOUNT_TYPE],max_length=20, default=ACCOUNT_TYPE.SAVINGS.value)
    branch_name = models.CharField(max_length=100, default='')

    def __str__(self):
        return str(self.account_holder_name)
    
    class Meta:

        constraints = [UniqueConstraint(fields=['account_number', "ifsc",'account'],
                                        
                                        name='bank_api_account'), ]

def validate_age(value):
    if   value > 70:
        raise ValidationError(
            ('Invalid age. Age must be between 0 and 70.'),
            params={'value': value},
        )
class NomineeDetails(models.Model):
    nominee_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account ,on_delete=models.CASCADE ,related_name="nomieedetails_account")
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    contact_no=PhoneNumberField()
    relation=models.CharField(choices=[(e.value, e.value) for e in RELATION],max_length=100,default=RELATION.SIBLINGS.value)
    date_of_birth = models.DateField(null=True, blank=True)
    age=models.IntegerField(default=0,validators=[validate_age])
    spouse_name=models.CharField(max_length=100,blank=True,null=True)
    aadhar_no = models.CharField(max_length=1000, null=True, blank=True)
    aadhar_verified = models.BooleanField(default=False)
    aadhar_meta_field = models.JSONField(null=True, blank=True)
    insurance_policy_selected=models.ForeignKey(InsuranceProduct, on_delete=models.PROTECT, related_name='nominee_insurance',
                                                null=True, blank=True)



    def __str__(self) -> str:
        return str(self.first_name)
    # class Meta:
    #     constraints = [UniqueConstraint(fields=['account', 'relation'],
                                        
    #                                     name='nominee_account'), ]

class AgentAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='agent_accounts',
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=255)
    agent_id = models.CharField(max_length=255, null=True, blank=True)
    alternate_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    house = models.CharField(max_length=255, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    education=models.CharField(choices=[(e.value, e.value) for e in AGENT_EDUCATION],max_length=100,default=AGENT_EDUCATION.GRADUATE.value,blank=True,null=True)
    occupation=models.CharField(choices=[(e.value, e.value) for e in AGENT_OCCUPATION],max_length=100,default=AGENT_OCCUPATION.OTHERS.value)
    aadhar_no = models.CharField(max_length=20, null=True, blank=True)
    pan_no = models.CharField(max_length=20, null=True, blank=True)
    status=models.CharField(choices=[(e.value, e.value) for e in AGENT_ACCOUNT_STATUS],max_length=100,default=AGENT_ACCOUNT_STATUS.ACCOUNT_DETAILS_ADDED.value,blank=True,null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='agent_accounts_created',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='agent_accounts_modified',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.full_name} ({self.user})"


class AgentBankAccount(models.Model):
    Agent_bank_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(AgentAccount ,on_delete=models.CASCADE ,related_name="bankaccount_agentaccount")
    verified = models.BooleanField(default=False)
    account_number = models.CharField(max_length=100)
    ifsc =models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=255)
    pan_number = models.CharField(max_length=20, null=True, blank=True)
    def __str__(self):
        return str(self.account_holder_name)


class NewAccount(models.Model):
    new_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    customer_id=models.CharField(max_length=12,unique=True)
    phone = PhoneNumberField(unique=True)
    pan_card_number=models.CharField(max_length=20, validators=[validate_pan_card])
    is_pan_verified=models.BooleanField(default=False)
    customer_name=models.CharField(max_length=255)
    lead = models.ForeignKey("onboarding_v2.LeadV2", on_delete=models.CASCADE, related_name='new_account_lead', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True )
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self): 
        return str(self.new_account_id )

class NewAccountDocument(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type =models.CharField(max_length=50, choices=[(e.value, e.value) for e in LEAD_DOCUMENT_TYPE], null=True, blank=True)
    file_name = models.CharField(max_length=225, blank=True, null=True)
    file = models.FileField(max_length=225,blank=False, null=False, upload_to=settings.SUBTASK_DOCUMENT)
    new_account = models.ForeignKey(NewAccount,on_delete=models.CASCADE,blank=True,null=True, related_name="new_account_document")
    status = models.CharField(max_length=50, choices=[(e.value, e.value) for e in NEW_ACCOUNT_STATUS], null=True, blank=True)
    source = models.CharField(max_length=100,choices=[(e.value, e.value) for e in NEW_LEAD_SOURCE], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='NEW_ACCOUNT_DOC_USER', on_delete=models.CASCADE, null=True, blank=True)

    def get_file_url(self):
        return self.file.url
    
    def __str__(self):
        return str(self.document_id)
