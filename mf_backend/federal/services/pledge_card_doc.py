from django.template.loader import get_template
import base64
import pdfkit
from application.service import ApplicationService
from ..models import Application
from application.serializers import ApplicationOverviewSerializer
from django.conf import settings
import ctypes


class PledgeCardCreation:
    def get_image(self, application_id):
        application = Application.objects.get(application_id=application_id)
        applicationData = ApplicationOverviewSerializer(application)

        htmlData = applicationData.data

        for k, v in htmlData["account"].items():
            htmlData["account__" + k] = v

        htmlData["account__created_at"] = ApplicationService().format_date(
            htmlData["account__created_at"].split("T")[0]
        )
        htmlData["account__year_of_birth"] = ApplicationService().format_date(
            htmlData["account__year_of_birth"].split("T")[0]
        )
        # htmlData["account__caste"] = htmlData["account__caste"].lower()
        htmlData["account__gender"] = htmlData["account__gender"].lower()

        htmlData["account_number"] = htmlData["account"]["bankaccount"][0][
            "account_number"
        ]

        htmlData["logo_path"] = settings.LOGO

        asset_dict = {}
        for i, a in enumerate(htmlData["asset"]):
            asset_dict[i + 1] = dict(a)
        htmlData["asset"] = asset_dict

        template = get_template("pledge_card.html")

        html = template.render(htmlData)

        # wkhtmltopdf = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"

        options = {
            "page-size": "A4",
            "margin-top": "5mm",
            "margin-right": "5mm",
            "margin-bottom": "5mm",
            "margin-left": "5mm",
            "enable-local-file-access": "",
            "encoding": "UTF-8",
        }

        pdf = pdfkit.from_string(
            html, False, options=options, configuration=pdfkit.configuration()
        )

        from wand.image import Image
        from wand.api import library


        # # Set the policy to allow reading and writing PDF files
        # library.MagickSetOption.restype = ctypes.c_int
        # library.MagickSetOption.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]

        # policy = b"PDF"
        # rules = b"read,write"
        # library.MagickSetOption(None, policy, rules)


        with Image(blob=pdf, format="pdf", resolution=300) as pdf:
            with pdf.convert("png") as img:
                # img.alpha_channel = False  # Ensure alpha channel is turned off
                # img.background_color = "white"
                # img.format = "png"
                return base64.b64encode(img.make_blob()).decode("utf-8")
