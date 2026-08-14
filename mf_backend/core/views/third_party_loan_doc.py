import pdfkit
from django.http.response import HttpResponseBase, HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.service.jofin_application_data import JoffinApplicationData
from instance import custom_response_obj


class ThirdPartyLoanDoc(View):
    permission_classes = [AllowAny]

    def get(self, request):
        application_id = request.GET.get('application_id')
        print(application_id)
        if not application_id:
            msg = custom_response_obj(message={'msg': 'Application id is required'}, code=400)
            return Response(msg, status=400)

        pdf, data = JoffinApplicationData().get_data(application_id=application_id)
        response = HttpResponse(content_type="application/pdf")
        filename = "{app_no}-{fn}_{ln}.pdf".format(
            app_no=data.get('application_number'),
            fn=data.get('first_name'),
            ln=data.get('last_name'),
        )
        response["Content-Disposition"] = 'attachment; filename="{filename}"'.format(
            filename=filename
        )
        response["Access-Control-Expose-Headers"] = 'Content-Disposition'
        response.write(pdf)
        return response
