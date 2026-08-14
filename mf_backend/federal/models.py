from django.db import models
import uuid

from application.models import Application
from account.models import Account
from django.conf import settings

   
class FederalBankApplication(models.Model):
    
    federal_application_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="federal_account", default=None)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="federal_application", default=None)
    
    ekyc_consent_given=models.BooleanField(default=False)
    ekyc_consent_given_at=models.DateTimeField(blank=True,null=True)
    
    name_dob_request_id=models.CharField(max_length=50,editable=False,blank=True,null=True)
    name_dob_status=models.CharField(max_length=50,editable=False,blank=True,null=True)
    name_dob_desc=models.CharField(max_length=50,editable=False,blank=True,null=True)
    
    ekyc_meta_response=models.JSONField(blank=True,null=True)
    name_dob_meta_response=models.JSONField(blank=True,null=True)
    dedupe_meta_response=models.JSONField(blank=True,null=True)
    pan_validation_meta_response=models.JSONField(blank=True,null=True)
    unofac_meta_response=models.JSONField(blank=True,null=True)
    is_existing_customer=models.BooleanField(blank=True,null=True)
    is_eligible=models.BooleanField(blank=True,null=True)

    ekyc_request_id=models.CharField(max_length=50,editable=False,blank=True,null=True)
    aadhar_rrn = models.CharField(max_length=50,editable=False,blank=True,null=True)
    ekyc_status = models.CharField(max_length=1,editable=False,blank=True,null=True)
    aua_specific_uid_token = models.CharField(max_length=100,editable=False,blank=True,null=True)
    masked_aadhaar_number_from_UIDAI=models.CharField(max_length=12,editable=False,blank=True,null=True)
    post_office=models.CharField(max_length=25,editable=False,blank=True,null=True)
    phone=models.CharField(max_length=12,editable=False,blank=True,null=True)
    house_no=models.CharField(max_length=50,editable=False,blank=True,null=True)
    street=models.CharField(max_length=100,editable=False,blank=True,null=True)
    state=models.CharField(max_length=50,editable=False,blank=True,null=True)
    vtc_name=models.CharField(max_length=25,editable=False,blank=True,null=True)
    photo=models.CharField(max_length=500,editable=False,blank=True,null=True)
    pincode=models.CharField(max_length=25,editable=False,blank=True,null=True)
    lamdmark=models.CharField(max_length=50,editable=False,blank=True,null=True)
    email=models.CharField(max_length=50,editable=False,blank=True,null=True)
    dob=models.CharField(max_length=25,editable=False,blank=True,null=True)
    name=models.CharField(max_length=50,editable=False,blank=True,null=True)
    gender=models.CharField(max_length=25,editable=False,blank=True,null=True)
    locality=models.CharField(max_length=50,editable=False,blank=True,null=True)
    careof=models.CharField(max_length=50,editable=False,blank=True,null=True)
    district=models.CharField(max_length=50,editable=False,blank=True,null=True)
    
    ddupe_request_id=models.CharField(max_length=50,editable=False,blank=True,null=True)
    ddupe_flag = models.CharField(max_length=5,editable=False,blank=True,null=True)
    kyc_flag = models.CharField(max_length=5,editable=False,blank=True,null=True)
    kyc_profile_flag = models.CharField(max_length=5,editable=False,blank=True,null=True)
    partial_kyc_flag = models.CharField(max_length=5,editable=False,blank=True,null=True)
    dob_flag = models.CharField(max_length=5,editable=False,blank=True,null=True)
    mobile_flag = models.CharField(max_length=5,editable=False,blank=True,null=True)
    nri_flag = models.CharField(max_length=5,editable=False,blank=True,null=True)
    minor_flag = models.CharField(max_length=5,editable=False,blank=True,null=True)
    ddupe_reference_id=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field1=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field2=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field3=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field4=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field5=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field6=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field7=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field8=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field9=models.CharField(max_length=25,editable=False,blank=True,null=True)
    reserve_field10=models.CharField(max_length=25,editable=False,blank=True,null=True)

    customer_id = models.CharField(max_length=50,blank=True,null=True)
    customer_name = models.CharField(max_length=50,blank=True,null=True)
    
    #{'PAN': 'BCHPA8315E', 'PANStatus': 'E', 'LastName': 'ALTAF', 'FirstName': 'ASIF', 'PANTitle': 'Shri', 'LastUpdateDate': '16/08/2017', 'NameOnCard': 'ASIF ALTAF', 'AadhaarSeededStatus': 'Y'}
    
    pan_request_id=models.CharField(max_length=50,editable=False,blank=True,null=True)
    pan_response_code=models.CharField(max_length=5,editable=False,blank=True,null=True)
    pan=models.CharField(max_length=10,editable=False,blank=True,null=True)
    pan_status=models.CharField(max_length=1,editable=False,blank=True,null=True)
    first_name=models.CharField(max_length=25,editable=False,blank=True,null=True)
    last_name=models.CharField(max_length=25,editable=False,blank=True,null=True)
    pan_title=models.CharField(max_length=10,editable=False,blank=True,null=True)
    last_update_date=models.DateField(editable=False,blank=True,null=True)
    name_on_card = models.CharField(max_length=50,editable=False,blank=True,null=True)
    aadhar_seeded_Status=models.CharField(max_length=1,editable=False,blank=True,null=True)
    
    unchck_request_id=models.CharField(max_length=50,editable=False,blank=True,null=True)
    unchck_status=models.CharField(max_length=1,editable=False,blank=True,null=True)
    unchk_msg=models.CharField(max_length=100,editable=False,blank=True,null=True)
    unchk_first_name=models.CharField(max_length=100,editable=False,blank=True,null=True)
    unchk_last_name=models.CharField(max_length=100,editable=False,blank=True,null=True)
    unchk_ind_address_note=models.CharField(max_length=100,editable=False,blank=True,null=True)
    
    gl_account_reference_id=models.CharField(max_length=100,editable=False,blank=True,null=True)
    
    solId = models.CharField(max_length=10,blank=True,null=True)
    sign_id = models.FileField(blank=True,null=True, upload_to=settings.SIGNATURE_DOCUMENT)
    agent_otp = models.IntegerField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modefied_at = models.DateTimeField(auto_now=True)
    
class SolidMapping(models.Model):
    solid_mapping_id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    solid=models.CharField(max_length=10,blank=False,null=False)
    branch_location=models.CharField(max_length=100,blank=False,null=False)
    
class StateCode(models.Model):
    state_code_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    state_name = models.CharField(max_length=100,blank=False,null=False)
    state_code = models.CharField(max_length=10,blank=False,null=False)

    def __str__(self) -> str:
        return self.state_code
    
    
class CityCode(models.Model):
    city_code_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    city_name = models.CharField(max_length=100,blank=False,null=False)
    city_code = models.CharField(max_length=10,blank=False,null=False)


    def __str__(self) -> str:
        return self.city_code
    


