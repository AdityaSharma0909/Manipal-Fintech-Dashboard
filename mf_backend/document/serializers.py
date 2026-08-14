import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile

from utils.constants import ApplicationType
from .models import Document
from application.models import LoanDocument, AssetDocuments
from lead.models import LeadDocument
from rest_framework import serializers
from users.serializers import   UserResponseSerializer


class FileLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model=Document
        fields=['file',]

class DocumentDisplaySerializer(serializers.ModelSerializer):
    uploaded_by=UserResponseSerializer()
    class Meta:
        model=Document
        fields="__all__"
class DocumentDisplayOverviewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Document
        exclude=["uploaded_by", ]

class DocumentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Document
        fields="__all__"


class AssetDocumentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=AssetDocuments
        fields=["asset_document_id","asset_document_type","file_name","file","asset"]

class DocumentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Document
        fields="__all__"

class LoanDocumentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=LoanDocument
        fields="__all__"

    def save(self):
        try:
            loan_doc=LoanDocument.objects.get(application__application_id=self.validated_data.get('application').application_id,
                                              document_type__in=["SIGNED_LOAN_DOCUMENT"])

            # Get the file data from validated_data
            file_data = self.validated_data.get('file')

            # Create a ContentFile instance to save the in-memory file data
            content_file = ContentFile(file_data.read())
            file_name = self.validated_data.get('file_name')
            loan_doc.file_name=file_name
            loan_doc.file.save(file_name,content_file, save=True)
            loan_doc.save()
            return loan_doc
        except ObjectDoesNotExist:
            loan_doc=LoanDocument(**self.validated_data)
            loan_doc.save()
            return loan_doc
        

class GetLoanDocumentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=LoanDocument
        fields="__all__"

class LeadDocumentSerializer(serializers.ModelSerializer):
   
    class Meta:
        model=LeadDocument
        fields="__all__"