# task/models.py
import uuid
from django.conf import settings
from django.db import models
from flows.models import Flow
from utils.constants import (
USER_TYPE, ENTITY_TYPE, PRIORITY_CHOICES, TASK_STATUS,
CONDITION, SUBTASK_STATUS, FLOW_STATUS, DOCUMENT_FLOW, FLOW_DOCUMENT_TYPE,
CENTRAL_OPS_STATUS,OTHER_DOCUMENTS,GENDER,APPROVAL_STATUS,
NEW_LEAD_TYPE,NEW_LOAN_TYPE,SOURCE_TYPE
)
from django.core.exceptions import ValidationError


class Task(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # tasks_id
    task_id = models.CharField(max_length=100, unique=True)
    task_summary = models.CharField(max_length=255)
    is_auto_reject = models.BooleanField(default=False)
    auto_reject_time = models.CharField(max_length=100, blank=True, null=True)
    total_reward_assigned = models.IntegerField(default=0)
    priority = models.CharField(max_length=10, choices=[(e.value, e.value) for e in PRIORITY_CHOICES], default='MEDIUM')

    upload_customer_data = models.FileField(upload_to='uploads/customers/', null=True, blank=True)
    upload_employee_file = models.FileField(upload_to='uploads/employees/', null=True, blank=True)

    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    team = models.CharField(max_length=100, blank=True)
    badge = models.CharField(max_length=100, blank=True)

    cumulative_amount = models.IntegerField(default=0)

    status = models.CharField(max_length=20, choices=[(e.value, e.value) for e in TASK_STATUS], default=TASK_STATUS.YET_TO_START.value)
    progress = models.PositiveIntegerField(default=0)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tasks_assigned', on_delete=models.SET_NULL, null=True, blank=True)
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tasks_created', on_delete=models.SET_NULL, null=True, blank=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tasks_modified', on_delete=models.SET_NULL, null=True, blank=True)

    flows = models.ManyToManyField(Flow, through='TaskFlow', related_name='tasks')

    def __str__(self):
        return f"{self.task_id} - {self.task_summary}"

class TaskFlow(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, related_name='task_flow_entries', on_delete=models.CASCADE)
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE)
    condition = models.CharField(max_length=20, choices=[(e.value, e.value) for e in CONDITION], default='MANDATORY')
    reward = models.IntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('task', 'flow')  # a given flow appears once per task in this model

    def __str__(self):
        return f"{self.task.task_id} - {self.flow.flow_id} ({self.condition})"


# class SubTask(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # sub_task_id
#     task = models.ForeignKey(Task, related_name='subtasks', on_delete=models.CASCADE)
#     customer_id = models.CharField(max_length=200)
#     contact_name = models.CharField(max_length=255)
#     organization_name = models.CharField(max_length=255, blank=True)
#     contact_no = models.CharField(max_length=50, blank=True)
#     address = models.TextField(blank=True)
#     assign_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_subtasks', on_delete=models.SET_NULL, null=True, blank=True)

#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subtasks_created', on_delete=models.SET_NULL, null=True, blank=True)
#     modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='subtasks_modified', on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return f"SubTask {self.id} for Task {self.task.task_id}"


class SubTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, related_name='subtasks', on_delete=models.CASCADE)
    sub_task_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    
    contact_person_name = models.CharField(max_length=150, null=True, blank=True)
    contact_person_number = models.CharField(max_length=15, null=True, blank=True)
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    unique_id = models.CharField(max_length=150, null=True, blank=True)


    type_of_user = models.CharField(max_length=20, choices=[(e.value, e.value) for e in USER_TYPE], null=True, blank=True)

    pincode = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)


    entity_type = models.CharField(max_length=20, choices=[(e.value, e.value) for e in ENTITY_TYPE], null=True, blank=True)

    organisation_name = models.CharField(max_length=255, null=True, blank=True)
    registered_mobile_number = models.CharField(max_length=15, null=True, blank=True)
    otp_verified = models.BooleanField(default=False)

    assign_to = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_subtasks', on_delete=models.SET_NULL, null=True, blank=True)
    
    verification_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[(e.value, e.value) for e in SUBTASK_STATUS], null=True, blank=True)
    decline_reason = models.TextField(null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='subtasks_created')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='subtasks_modified')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sub_tasks'
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"{self.sub_task_id} - {self.organisation_name or 'Unnamed'}"


class SubTaskTracker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subtask = models.ForeignKey(SubTask, related_name='trackers', on_delete=models.CASCADE)
    flow = models.ForeignKey(Flow, related_name='subtasks_flow_tracker', on_delete=models.CASCADE)
    flow_status = models.CharField(max_length=50, choices=[(e.value, e.value) for e in FLOW_STATUS], null=True, blank=True)
    progress = models.IntegerField(default=0)
    step_timestamps = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='subtasks_tracker_created')
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='subtasks_tracker_modified')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    central_ops_status = models.CharField(max_length=50, choices=[(e.value, e.value) for e in CENTRAL_OPS_STATUS],default="PENDING")
    central_ops_user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='subtasks_tracker_central_ops')
    central_ops_remarks = models.TextField(null=True,blank=True)
    reward = models.IntegerField(default=0)
    is_last = models.BooleanField(default=False)

    is_pan_verify = models.BooleanField(default=False)
    is_zoop_pan_verify = models.BooleanField(default=False)
    pan_otp = models.CharField(max_length=6, null=True, blank=True)
    pan_otp_created_at = models.DateTimeField(null=True, blank=True)
    pan_number = models.CharField(max_length=20, null=True, blank=True)
    aadhar_number = models.CharField(max_length=20, null=True, blank=True)
    is_aadhar_verify = models.BooleanField(default=False)
    is_face_match_verify = models.BooleanField(default=False)
    other_document = models.CharField(max_length=50, choices=[(e.value, e.value) for e in OTHER_DOCUMENTS], null=True, blank=True)
    other_document_verified = models.BooleanField(default=False)
    full_name = models.CharField(max_length=150, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50, choices=[(e.value, e.value) for e in GENDER], null=True, blank=True)
    father_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    whatsapp_number = models.CharField(max_length=15, null=True, blank=True)
    is_whatsapp_verified = models.BooleanField(default=False)
    profession = models.CharField(max_length=100, null=True, blank=True)
    permanent_address = models.TextField(null=True, blank=True)
    permanent_address_pincode = models.CharField(max_length=10, null=True, blank=True)
    permanent_address_state = models.CharField(max_length=100, null=True, blank=True)
    permanent_address_city = models.CharField(max_length=100, null=True, blank=True) 
    permanent_address_district = models.CharField(max_length=100, null=True, blank=True)
    current_address_state = models.CharField(max_length=100, null=True, blank=True)
    current_address_district = models.CharField(max_length=100, null=True, blank=True)
    current_address_city = models.CharField(max_length=100, null=True, blank=True)
    current_address_pincode = models.CharField(max_length=10, null=True, blank=True)
    current_address = models.TextField(null=True, blank=True)

    product_category = models.CharField(
        max_length=100,
        choices=[(e.value, e.value) for e in NEW_LEAD_TYPE],
        null=True,
        blank=True
    )

    
    product_sub_category = models.CharField(
        max_length=100,
        choices=[(e.value, e.value) for e in NEW_LOAN_TYPE],
        null=True,
        blank=True
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    step_number = models.IntegerField(blank=True,null=True)
    current_review_step = models.PositiveIntegerField(default=0)  # Which step is under review
    all_steps_approved = models.BooleanField(default=False)
    lead_source = models.CharField(
        max_length=50,
        choices=[(e.value, e.value) for e in SOURCE_TYPE],
        null=True,
        blank=True
    )
    customer_id = models.CharField(max_length=100, null=True, blank=True)
    loan_date = models.DateField(null=True, blank=True)
    loan_account_number = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=150, null=True, blank=True)
    lead_id = models.UUIDField(null=True, blank=True)
    lead_type = models.CharField(
        max_length=50,
        choices=[(e.value, e.value) for e in NEW_LEAD_TYPE],
        null=True,
        blank=True
    )



    def __str__(self):
        return f"Action on SubTask {self.subtask.sub_task_id} by {self.created_by}"
    

class SubTaskDocument(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_flow = models.CharField(max_length=50, choices=[(e.value, e.value) for e in DOCUMENT_FLOW], null=True, blank=True)
    document_type =models.CharField(max_length=50, choices=[(e.value, e.value) for e in FLOW_DOCUMENT_TYPE], null=True, blank=True)
    file_name = models.CharField(max_length=225, blank=True, null=True)
    file = models.FileField(max_length=225,blank=False, null=False, upload_to=settings.SUBTASK_DOCUMENT)
    subtask = models.ForeignKey(SubTask,on_delete=models.CASCADE,blank=True,null=True, related_name="subtask_document")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='FLOW_DOC_USER', on_delete=models.CASCADE, null=True, blank=True)

    def get_file_url(self):
        return self.file.url
    
    def __str__(self):
        return str(self.document_id)








class SubTaskApproval(models.Model):
    """
    Tracks approval status for each flow step in a subtask tracker.
    One record per step per subtask tracker.
    """
    
    class ApprovalStatus(models.TextChoices):
        NOT_SUBMITTED = 'NOT_SUBMITTED', 'Not Submitted'
        SUBMITTED = 'SUBMITTED', 'Submitted'
        APPROVED = 'APPROVED', 'Approved'
        CORRECTION_NEEDED = 'CORRECTION_NEEDED', 'Correction Needed'
        REVIEWED = "REVIEWED"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Quick check for completion
    subtask_tracker = models.ForeignKey(
        SubTaskTracker, 
        related_name='step_approvals', 
        on_delete=models.CASCADE
    )
    flow_step = models.ForeignKey(
        'flows.FlowStep',  # Assuming FlowStep model exists in flows app
        related_name='approvals',
        on_delete=models.CASCADE
    )
    step_order = models.PositiveIntegerField()  # Denormalized for quick sorting
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.NOT_SUBMITTED
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='approved_steps',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flow_step_approvals'
        ordering = ['step_order']
        unique_together = ('subtask_tracker', 'flow_step')
        indexes = [
            models.Index(fields=['subtask_tracker', 'approval_status']),
            models.Index(fields=['step_order']),
        ]
    
    def __str__(self):
        return f"Step {self.step_order} - {self.approval_status} - {self.subtask_tracker.subtask.sub_task_id}"


class StepCorrection(models.Model):
    """
    Tracks correction history for flow steps.
    Multiple records possible per step (if sent back multiple times).
    """
    
    class CorrectionStatus(models.TextChoices):
        PENDING_CORRECTION = 'PENDING_CORRECTION', 'Pending Correction'
        RESUBMITTED = 'RESUBMITTED', 'Resubmitted'
        RESOLVED = 'RESOLVED', 'Resolved'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flow_step_approval = models.ForeignKey(
        SubTaskApproval,
        related_name='corrections',
        on_delete=models.CASCADE
    )
    reason = models.CharField(max_length=100)  # From predefined list
    comment = models.TextField(blank=True, null=True)  # Optional ops comment
    corrected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='corrections_made',
        on_delete=models.SET_NULL,
        null=True
    )
    corrected_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=CorrectionStatus.choices,
        default=CorrectionStatus.PENDING_CORRECTION
    )
    resubmitted_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'step_corrections'
        ordering = ['-corrected_at']
        indexes = [
            models.Index(fields=['flow_step_approval', 'status']),
            models.Index(fields=['corrected_at']),
        ]
    
    def __str__(self):
        return f"Correction for Step {self.flow_step_approval.step_order} - {self.status}"
