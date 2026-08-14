from django.db import models
import uuid
from utils.constants import YES_OR_NO , POSITIVE_OR_NEGATIVE
from application.models import Application
from users.models import User

class TeleVerification(models.Model):
    tele_verification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    application = models.OneToOneField(Application, on_delete=models.DO_NOTHING, related_name="tele_application")
    report_in_brief = models.TextField()
    location_captured = models.TextField()
    picture_captured = models.CharField(choices=[(e.value, e.value) for e in YES_OR_NO], max_length=10)
    observation = models.CharField(choices=[(e.value, e.value) for e in POSITIVE_OR_NEGATIVE], max_length=10)
    observation_comment = models.TextField(null=True , blank=True)
    residential_stability = models.CharField(choices=[(e.value, e.value) for e in POSITIVE_OR_NEGATIVE], max_length=10)
    residential_stability_comment = models.TextField(null=True , blank=True)
    business_stability = models.CharField(choices=[(e.value, e.value) for e in POSITIVE_OR_NEGATIVE], max_length=10)
    business_stability_comment = models.TextField(null=True , blank=True)
    no_of_similar_business = models.IntegerField()
    suppliers_customer_feeedback = models.TextField()
    external_income = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)
    modified_at=models.DateTimeField(auto_now_add=True,null=True, blank=True)

    def __str__(self):
        return str(self.tele_verification_id)


class Videokyc(models.Model):
    video_kyc_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    entity_id = models.IntegerField()
    client_user_id = models.IntegerField(unique=True)
    product_type = models.IntegerField(choices=[(4, "Individual Guest Chat"), (5, "Group Guest Chat")])
    first_name = models.CharField(max_length=64)
    customer_id = models.CharField(max_length=20, blank=True, null=True)
    tracking_id = models.CharField(max_length=100, blank=True, null=True)
    application_id = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=256, blank=True, null=True)
    product = models.CharField(max_length=100, blank=True, null=True)
    other_info = models.TextField(blank=True, null=True)
    user_photo = models.TextField(blank=True, null=True)  # Base64 encoded image
    status_url = models.URLField(blank=True, null=True, max_length=2000)
    use_case = models.IntegerField(choices=[(1, "VideoKYC")])
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    def __str__(self):
        return str(self.tele_verification_id)
