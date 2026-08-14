from django.db import models


class LeadStatusChoices(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    SUCCESS = 'Success', 'Success'
    FAILED = 'Failed', 'Failed'
    DUPLICATE = 'Duplicate', 'Duplicate'
    REJECTED = 'Rejected', 'Rejected'


class Branch(models.Model):
    branch_id = models.IntegerField(primary_key=True)
    branch_name = models.CharField(max_length=255)
    branch_code = models.CharField(max_length=50, db_index=True)
    pincode = models.CharField(max_length=10)
    district_id = models.IntegerField(db_index=True, null=True, blank=True)


    class Meta:
        db_table = 'bajaj_branch_detail'
        verbose_name_plural = 'Branches'

    def __str__(self):
        return f"{self.branch_code} - {self.branch_name}"


class Lead(models.Model):
    full_name = models.CharField(max_length=80)
    mobile_no = models.CharField(max_length=15, db_index=True)
    pincode = models.CharField(max_length=10)
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    # bank_id = models.BigIntegerField()
    crm_id = models.CharField(max_length=100, blank=True, null=True, db_index=True) # Bajaj External CRM Reference ID
    api_message = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    branch = models.CharField(max_length=100) # Local branch code/id
    lead_status = models.CharField(
        max_length=20,
        choices=LeadStatusChoices.choices,
        default=LeadStatusChoices.FAILED
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bajaj_lead_integration'
        indexes = [
            models.Index(fields=['mobile_no', 'lead_status']),
        ]

    def __str__(self):
        return f"Lead {self.id} - {self.full_name}"


class LeadAudit(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='audits')
    encrypted_request = models.TextField()
    encrypted_response = models.TextField(blank=True, null=True)
    plain_request = models.TextField()
    plain_response = models.TextField(blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bajaj_lead_audit_logs'

    def __str__(self):
        return f"Audit for Lead ID {self.lead_id or 'Unknown'}"
