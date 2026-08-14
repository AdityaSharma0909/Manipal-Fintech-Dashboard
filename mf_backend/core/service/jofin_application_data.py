import datetime

import pdfkit
from django.template.loader import get_template

from application.models import Application
import num2words

from radian_backend import settings


class JoffinApplicationData:

    def get_data(self, application_id):
        application=Application.objects.get(application_id=application_id)
        end_date=application.created_at
        address=application.account.user_addresse.all().first()

        html_data={
            'date':str(application.created_at.date()),
            'username':application.account.user.first_name +' '+application.account.user.last_name,
            'last_name':application.account.user.last_name,
            'loan_amount':application.loan_amount,
            'loan_amount_words':num2words.num2words(application.loan_amount),
            'address':address.street_name,
            'repayment_date':str(end_date.date()),
            'month':'JAN',
            'year':'2024',
            'first_name':application.account.user.first_name,
            'application_number':application.application_number,
            'logo_path':settings.LOGO,
            'prefix':'Mr' if application.account.gender=='MALE' else application.account.gender=='FEMALE',

        }
        template = get_template("application/joffin_loan_doc.html")
        html = template.render(html_data)
        # Renders the template with the context data.
        options = {
            "page-size": "A4",
            "margin-top": "5mm",
            "margin-right": "5mm",
            "margin-bottom": "5mm",
            "margin-left": "5mm",
            "enable-local-file-access": "",
            "encoding": "UTF-8",
        }
        pdf = pdfkit.from_string(html, False, options=options, configuration=pdfkit.configuration())
        return pdf, html_data
