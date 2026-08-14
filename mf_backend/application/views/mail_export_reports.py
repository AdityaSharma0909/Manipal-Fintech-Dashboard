from threading import Thread

from rest_framework.views import APIView

from application.services.mail_reports_data import MailExportData

from utility.api_framework import ApiFramework
from utility.common_utils import custom_response_obj


class MailReportView(APIView, ApiFramework):
    serializer=None

    def process(self):
        mail_sender=MailExportData()
        thread=Thread(target=mail_sender.process)
        thread.start()
        return custom_response_obj(message={'msg':'Request registered, Report will be sent to you in few minutes'}, code=200)


    def get(self, request):
        return self.main()
