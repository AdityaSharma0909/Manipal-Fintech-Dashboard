from django.db import models

# Create your models here.
import uuid
from application.models import Application
from django.conf import settings

class ScoreMeBankAnalysis(models.Model):
    score_me_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    application = models.ForeignKey(Application, related_name="score_me_application", on_delete=models.CASCADE)
    
    reference_id = models.CharField(max_length=64, null=True, blank=True)
    json_url = models.TextField(null=True, blank=True)
    excel_url = models.TextField(null=True, blank=True)
    
    cash_flow = models.FloatField(null=True, blank=True)
    average_monthly_balance = models.FloatField(null=True, blank=True)
    leverage_to_income = models.FloatField(null=True, blank=True)
    
    webhook_response = models.TextField(null=True, blank=True)