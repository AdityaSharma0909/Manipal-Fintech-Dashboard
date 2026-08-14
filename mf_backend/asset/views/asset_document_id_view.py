import requests
from rest_framework.views import APIView

from asset.services.asset_doc_service import AssetDocsService
from utility.api_framework import ApiFramework


class AssetDocumentIdUtil(ApiFramework):

    def __init__(self, data):
        super().__init__()
        self.__data=data
    def process(self):
        return AssetDocsService().delete_doc_id(self.__data.get('asset_document_id'))


class DeleteAssetDocumentView(APIView):

    def delete(self, request):
        data={'asset_document_id':request.query_params.get('asset_document_id')}
        return AssetDocumentIdUtil(data=data).main()