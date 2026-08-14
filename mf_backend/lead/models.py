""" All Lead related Models goes here"""

import uuid
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from users.models import User
from lender.models import Lender
from account.models import Account
from utils.constants import LEAD_STATUS, LEAD_TYPE, LEAD_SOURCE, LENDER , LENDING_TYPE , LEAD_DOCUMENT, NEW_LEAD_SOURCE, NEW_LEAD_TYPE , NEW_LOAN_TYPE , NEW_LEAD_STATUS,SOURCE_TYPE
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.conf import settings


# Create your models here.
class Lead(models.Model):
    """Creating Leads for each customer before creating Accounts"""

    lead_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100 ,null=True,blank=True)
    # TODO: lead_type is not used anywhere, can be converted to PERSONAL_LOAN or GOLD_LOAN instead of FRESH or TAKEOVER
    lead_type = models.CharField(choices=[(e.value, e.value) for e in LEAD_TYPE],max_length=100,default=LEAD_TYPE.FRESH.value)
    address_line = models.TextField()
    email = models.EmailField(blank=True,null=True)
    source = models.CharField(choices=[(e.value, e.value) for e in LEAD_SOURCE],max_length=100,default=LEAD_SOURCE.LOAN_OFFICER_APP.value)
    product_name=models.CharField(max_length=100, blank=True, null=True)
    pincode=models.CharField(max_length=10 ,blank=True,null=True)
    city=models.CharField(max_length=255,blank=True,null=True)
    state=models.CharField(max_length=255,blank=True,null=True)
    country=models.CharField(max_length=255,blank=True,null=True)
    phone = PhoneNumberField(unique=True)
    dob=models.DateField(null=True, blank=True)
    pan_number=models.CharField(max_length=100,null=True, blank=True)
    is_phone_verified=models.BooleanField(default=False)
    comments=models.TextField(blank=True, null= True)
    # lender_type=models.CharField(max_length=100, null=True, blank=True, choices=[(e.value, e.value) for e in LENDER])
    lender = models.ForeignKey(Lender, blank=True, null= True, on_delete=models.CASCADE, related_name="lead_lenders",)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    status=models.CharField(choices=[(e.value, e.value) for e in LEAD_STATUS],default=LEAD_STATUS.NEW_LEAD.value,max_length=40)
    assigned_to = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="lead_user",
    )
    account=models.OneToOneField(Account, on_delete=models.CASCADE, null=True, blank=True, related_name="lead_account")
    lending_type=models.CharField(choices=[(e.value , e.value) for e in LENDING_TYPE],max_length=20)

    refered_by = models.ForeignKey(User, blank=True, null= True, on_delete=models.CASCADE, related_name="lead_refered_by",)

    created_by = models.ForeignKey(User, blank=True, null= True, on_delete=models.CASCADE, related_name="lead_created_by",)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    def phone_to_str(self):
        """Convert the type field to its string representation
        (the boneheaded way).
        """
        return str(self.phone)
        

    def __str__(self) -> str:
        return str(self.first_name).title() +" " +str(self.last_name).title()
    
class LeadDocument(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=255,default="no_type", choices=LEAD_DOCUMENT, blank=True, null=True)
    file_name = models.CharField(max_length=225, blank=True, null=True)
    file = models.FileField(max_length=225,blank=False, null=False, upload_to=settings.LEAD_DOCUMENT)
    # url = models.CharField(max_length=500, blank=True, null=True)
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE,blank=True,null=True, related_name="lead_document")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def get_file_url(self):
        return self.file.url
    
    def __str__(self):
        return str(self.document_id)
    

@receiver(pre_delete, sender=LeadDocument)
def loan_document_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)




class NewLead(models.Model):
    """Model to store new leads generated from external sources"""

    new_lead_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100)
    phone = PhoneNumberField()
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    email = models.EmailField(blank=True,null=True)
    source = models.CharField(choices=[(e.value, e.value) for e in NEW_LEAD_SOURCE],max_length=100)
    loan_type = models.CharField(choices=[(e.value, e.value) for e in NEW_LOAN_TYPE],max_length=100)
    lead_type = models.CharField(choices=[(e.value, e.value) for e in NEW_LEAD_TYPE],max_length=100, blank=True, null=True)
    status = models.CharField(choices=[(e.value, e.value) for e in NEW_LEAD_STATUS],default=LEAD_STATUS.NEW_LEAD.value,max_length=40)
    lead_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, blank=True, null= True, on_delete=models.CASCADE, related_name="new_lead_created_by")
    modified_by = models.ForeignKey(User, blank=True, null= True, on_delete=models.CASCADE, related_name="new_lead_modified_by")
    source_type = models.CharField(
        choices=[(e.value, e.value) for e in SOURCE_TYPE],
        max_length=50,
        blank=True,
        null=True
    )
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    address_line = models.TextField(blank=True, null=True)


    def phone_to_str(self):
        """Convert the type field to its string representation
        (the boneheaded way).
        """
        return str(self.phone)
        

    def __str__(self) -> str:
        name = (self.full_name or "").strip()
        if name:
            return name.title()
        return str(self.new_lead_id)
