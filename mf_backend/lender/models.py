from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

import uuid
# Create your models here.

class Lender(models.Model):
    lender_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: remove null=True & blank=True of below lender_code field
    lender_code=models.CharField(max_length=255, unique=True, null=True, blank=True)
    lender_name=models.CharField(max_length=255)
    lender_address=models.CharField(max_length=255)
    created_At = models.DateTimeField(auto_now_add=True)
    modified_At = models.DateTimeField(auto_now=True)
  


    def __str__(self) -> str:
        return str(self.lender_name)
    
class LenderBranch(models.Model):
    lenderbranch_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lender=models.ForeignKey(Lender,on_delete=models.CASCADE,related_name="lender_lenderbranch")
    name=models.CharField(max_length=255)
    address=models.CharField(max_length=255)
    phone=PhoneNumberField()
    created_At = models.DateTimeField(auto_now_add=True)
    modified_At = models.DateTimeField(auto_now=True)
     
    def __str__(self) -> str:
        return str(self.name)

class LenderBranchMapping(models.Model):
    lenderbranchmapping_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lenderbranch=models.ForeignKey(LenderBranch,on_delete=models.CASCADE,related_name="lenderbranch_lenderbranchmapping")
    lender=models.ForeignKey(Lender,on_delete=models.CASCADE,related_name="lender_lenderbranchmapping")
    created_At = models.DateTimeField(auto_now_add=True)
    modified_At = models.DateTimeField(auto_now=True)
     


