from ..serializers import AssetDocumentSerializer
from  rest_framework.validators import ValidationError
from utils.constants import DOCUMENT_TYPE

from ..models import Document

class AssetDocumentUtils:
    def __init__(self, user):
        self.__user = user

    def upload_document_new(self, file,document_type,application,asset):
        try:

            
            payload = {
                "asset_document_type":document_type,
                "file_name":str(file.name),
                "application":application,
                "asset":asset,
                "uploaded_by": self.__user.user_id,
                "file":file
            }

            document_serialized = AssetDocumentSerializer(data=payload)
            return document_serialized
            
            
        except Exception as e:
            raise e