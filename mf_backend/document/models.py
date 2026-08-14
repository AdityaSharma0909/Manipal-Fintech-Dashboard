from __future__ import unicode_literals, absolute_import
from django.db import models
from utils import constants
from django.conf import settings
import uuid
from users.models import User
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint
# Receive the pre_delete signal and delete the file associated with the model instance.
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver


def file_size(value):
    limit =  1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 1 MiB.')



class Document(models.Model):
    document_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=255,default="no_type", choices=constants.DOCUMENT_TYPE, blank=True, null=True)
    file_name = models.CharField(max_length=225, blank=True, null=True)
    file = models.FileField(max_length=225,blank=False, null=False, upload_to=settings.ACCOUNT_DOCUMENT)
    # url = models.CharField(max_length=500, blank=True, null=True)
    account = models.ForeignKey("account.Account",on_delete=models.CASCADE,blank=True,null=True, related_name="document_account")
    is_password=models.BooleanField(blank=True,null=True)
    password = models.CharField(max_length=32, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, related_name='DOC_USER', on_delete=models.CASCADE, null=True, blank=True)

    def get_file_url(self):
        return self.file.url
    
    def __str__(self):
        return str(self.document_id)
    
    class Meta:
        
        constraints = [UniqueConstraint(fields=['document_type', 'account'],
                                        
                                        name='document_type_account'), ]
    


@receiver(pre_delete, sender=Document)
def document_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
