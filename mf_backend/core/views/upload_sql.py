from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utility.e2e_utility import MinioUtility


class UploadDocs(APIView):

    permission_classes = [AllowAny]
    def post(self, request):

        data=request.data
        print(data)
        resp=MinioUtility().put_objects(file=data.get('file'),path='db_backup')
        return Response(resp, status=200)