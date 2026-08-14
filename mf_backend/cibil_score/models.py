from django.db import models
from application.models import Application
from users.models import User
import uuid
from utils.constants import YES_OR_NO

class CibilScore(models.Model):
    cibil_score_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    application = models.ForeignKey(Application, related_name="cibil_score_application", on_delete=models.CASCADE)

    cb_score = models.IntegerField(blank=True,null=True)
    obligation = models.IntegerField(blank=True,null=True)
    existing_loan_amount = models.IntegerField(blank=True,null=True)
    emi_of_existing_loan = models.IntegerField(blank=True,null=True)
    no_of_loans_running = models.IntegerField(blank=True,null=True)
    no_of_loans_closed_in_last_1_year = models.IntegerField(blank=True,null=True)
    any_loan_applied_in_last_30_days = models.CharField(choices=[(e.value , e.value) for e in YES_OR_NO], max_length=20)

    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="cibil_score_created_by",blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)
    modified_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)

    def __str__(self):
        return str(self.cibil_score_id)