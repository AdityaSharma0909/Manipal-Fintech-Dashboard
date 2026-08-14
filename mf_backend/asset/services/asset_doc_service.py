from document.serializers import AssetDocumentSerializer
from utility.crud_helper import CrudHelper
from application.models import AssetDocuments
from utility.common_utils import custom_response_obj

class AssetDocsService:

    crud_helper=CrudHelper(AssetDocumentSerializer)


    def delete_doc_id(self, delete_id):
        return self.crud_helper.delete_obj(delete_id)
    
    @staticmethod
    def get_asset_documents_by_loan_id(loan_id):
        try:
            asset_documents = AssetDocuments.objects.filter(asset__application__loan_application__loan_id=loan_id)
            serialized_data = AssetDocumentSerializer(asset_documents, many=True).data
            return custom_response_obj(message={"asset_documents": serialized_data}, code=200)
        except Exception as e:
            return custom_response_obj(message=str(e), code=400)