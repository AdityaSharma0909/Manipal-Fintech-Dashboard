import uuid
from django.conf import settings
from django.db import models

class Flow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # flows_id
    flow_id = models.CharField(max_length=100, unique=True)
    flow_description = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    expected_duration = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='flows_created', on_delete=models.SET_NULL, null=True, blank=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='flows_modified', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.flow_id} - {self.flow_description}"


class FlowStep(models.Model):
    """
    Each flow has 3 or more steps; these are simple charfields with an order.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flow = models.ForeignKey(Flow, related_name='flow_steps', on_delete=models.CASCADE)
    step_order = models.PositiveIntegerField(default=0)
    step_description = models.CharField(max_length=255)

    class Meta:
        ordering = ['step_order']

    def __str__(self):
        return f"{self.flow.flow_id} - Step {self.step_order}: {self.step_description}"
