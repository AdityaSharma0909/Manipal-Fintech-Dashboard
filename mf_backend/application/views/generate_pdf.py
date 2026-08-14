from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from django.template import Template, Context
from django.http import HttpResponse

import pdfkit
import json
from rest_framework.permissions import AllowAny


class Generate_pdf(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('template')
        
        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            file_content = file_obj.read().decode('utf-8')
            template = Template(file_content)

            data = request.data.get('data',{})
            context = json.loads(data)
            # context = {"date": "2024-06-26","application_number": "123456789","loan_amount": "50000","customer_name":"John Doe"}  # example context
            rendered_template = template.render(Context(context))

            options = {
                "page-size": "A4",
                "margin-top": "5mm",
                "margin-right": "5mm",
                "margin-bottom": "5mm",
                "margin-left": "5mm",
                "enable-local-file-access": "",
                "encoding": "UTF-8",
            }

            pdf = pdfkit.from_string(rendered_template, False, options=options)

            # Create a response with the generated PDF
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="output.pdf"'  
            return response

            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
