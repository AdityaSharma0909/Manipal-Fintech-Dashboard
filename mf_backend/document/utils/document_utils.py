from application.models import LoanDocument
from utils.constants import ApplicationType
from ..serializers import DocumentSerializer,LoanDocumentSerializer
from  rest_framework.validators import ValidationError
from ..models import Document

class DocumentUtils:
    def __init__(self, user):
        self.__user = user

    def upload_document(self, file,document_type):
        try:
            payload = {
                "document_type":document_type,
                "file_name":str(file.name),
                "uploaded_by": self.__user.user_id,
                "file":file
            }

            document_serialized = DocumentSerializer(data=payload)
            
            if document_serialized.is_valid():
                doc = document_serialized.save()
                return doc
            
            raise ValidationError (document_serialized.errors)
        except Exception as e:
            raise e
    def upload_document_new(self, file,document_type,account):
        try:

            payload = {
                "document_type":document_type,
                "file_name":str(file.name),
                "account":account,
                "uploaded_by": self.__user.user_id,
                "file":file
            }

            document_serialized = DocumentSerializer(data=payload)
            return document_serialized
            
            
        except Exception as e:
            raise e
    
    def upload_loan_document_new(self, file,application, document_type):
        try:

            payload = {
                "document_type": document_type,
                "file_name":str(file.name),
                "application":application,
                "uploaded_by": self.__user.user_id,
                "file":file
            }
            document_serialized = LoanDocumentSerializer(data=payload, context={'content':file.content_type})
            return document_serialized
            
            
        except Exception as e:
            raise e


    def update_document(self, file, document_type, document_id,file_name):
        # try:
        #     document = Document.objects.get(document_id=document_id, document_type=document_type)
        #     document.delete()
        # except Document.DoesNotExist:
        #     pass

        if file:
            document = Document.objects.get(document_id=document_id, document_type=document_type)
            payload = {
                "document_type" : document_type,
                "file_name" : str(file_name) + "_" + str(document_type),
                "file" : file,
            }

            document_serialized = DocumentSerializer(document,data=payload, partial=True)
            if document_serialized.is_valid():
                document_serialized.save()
                pass
            else:
                raise ValidationError (document_serialized.errors)
            return document_serialized.data

    def verify_all_takeover_loan_documents(self, application_id):
        data = list(LoanDocument.objects.values_list('document_type', flat=True).filter(application__application_type=ApplicationType.TAKEOVER.value,
                                  application__application_id=application_id))



        count=0
        loan_docs=("EXISTING_LOAN_PROOF","BT_UNDERTAKING","SECURITY_CHEQUE")
        data=list(set(data))
        for i in data:

            if i in loan_docs:
                count+=1
        if count==3:
            return True
        else:
            return False
