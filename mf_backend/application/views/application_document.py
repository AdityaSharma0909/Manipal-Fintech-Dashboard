from application.models import ApplicationDocument , Application
from application.serializers import ApplicationDocSerializer
from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from utils.constants import APPLICATION_STATUS , APPLICATION_DOCUMENT
import traceback
from django.core.exceptions import ObjectDoesNotExist

class ApplicationDocumentView(APIView):
    def post(self,request):
        try:
            user = request.user
            data = request.data

            application_id = request.GET.get("application_id", "")
            if not application_id:
                return HttpResponse.BadRequest("Application not found")
            
            application = Application.objects.get(application_id=application_id)

            file = request.FILES.get('file')
            if not file:
                return HttpResponse.BadRequest({'error': 'No file uploaded'})
            
            doc_type=request.data.get('document_type')
            if not doc_type:
                return HttpResponse.BadRequest({'error': 'No Document Type added'})
            file_name=file.name
            data["file_name"] = file_name
            data["uploaded_by"] = str(user.user_id)
            data["application"] = application.application_id
            serializer = ApplicationDocSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                required_doc_types = [
                    "OWN_HOUSE_PROOF",
                    "BUSINESS_PROOF",
                    "POST_DATED_CHEQUE",
                    "VINTAGE_PROOF"
                ]
                existing_doc_types = set(application.application_document.filter(
                    document_type__in=required_doc_types
                ).values_list('document_type', flat=True))
                    
                if set(required_doc_types).issubset(existing_doc_types) and application.status == APPLICATION_STATUS.LOAN_AMOUNT_ADDED.value:
                    application.status = APPLICATION_STATUS.PROOF_DOCUMENTS_UPLOADED.value
                    application.save() 
                return HttpResponse.Success({"application_doc": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def get(self, request):
        try:
            application =Application.objects.get(application_id=request.GET.get("application_id", ""))
            
            if application:
                app_doc = ApplicationDocument.objects.filter(application=application)
                serializer = ApplicationDocSerializer(app_doc , many=True)
                return HttpResponse.Success({"application_doc": serializer.data})
            else:
                app_docs = ApplicationDocument.objects.all()
                serializer = ApplicationDocSerializer(app_docs, many=True)
                return HttpResponse.Success({"application_doc": serializer.data})
        
        except ApplicationDocument.DoesNotExist:
            return HttpResponse.BadRequest("Application Document not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
    def delete(self, request, *args, **kwargs):
        try:
            app_doc = ApplicationDocument.objects.get(
                document_id = request.GET.get('document_id',"")
            )
            app_doc.delete()
            return HttpResponse.Success({"msg": 'Deleted document successfully'})
        except ObjectDoesNotExist:
            return HttpResponse.BadRequest("Document not found")
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
        
    