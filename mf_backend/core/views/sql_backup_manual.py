import subprocess

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.service.database_backup import BackDatabase
from utility.e2e_utility import MinioUtility


class UploadBackup(APIView):

    permission_classes = [AllowAny]
    def post(self, request):
        BackDatabase().backup()
        return Response(status=204)