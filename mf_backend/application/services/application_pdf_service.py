from django.template.loader import get_template
import os
import pdfkit
from application.service import ApplicationService
from ..serializers import ApplicationOverviewSerializer
from django.conf import settings
from utils.envSetup import environment


class ApplicationPdfGeneration:

    def generate(self, application):

        # print(application.status)
        applicationData = ApplicationOverviewSerializer(application)
        htmlData = applicationData.data
        # htmlData["base_dir"] = settings.BASE_DIR
        # htmlData["media_base_url"] = environment.BASE_URL

        if htmlData["goods"]:
            goodsMap = {}
            for good in htmlData["goods"]:
                good["total_price"] = round(good["quantity"] * good["goods_price"], 2)
                goodsMap["goods__" + good["goods_id"]] = dict(good)
            htmlData["goods"] = goodsMap
        else:
            htmlData["goods"] = {}

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

        profilePath = os.path.join(
            settings.MEDIA_ROOT, htmlData["account"]["profile_photo"]["file_name"]
        )

        htmlData["profile_picture_path"] = profilePath
        for k, v in htmlData["account"]["user"].items():
            htmlData["account__user__" + k] = v
        htmlData["created_at"] = ApplicationService().format_date(
            htmlData["created_at"].split("T")[0]
        )
        bankaccounts = {}
        address = {}
        documents = {}

        for i in htmlData["account"]["documents"]:
            i = dict(i)
            documents[i["document_type"]] = i

        for k, v in documents.items():
            v["file"] = "http://101.53.135.26:8000" + v["file"]

        for i in htmlData["account"]["bankaccount"]:
            i = dict(i)
            bankaccounts[i["account_number"]] = i
        for i in htmlData["account"]["address"]:
            i = dict(i)
            i["address_type"] = i["address_type"].split("_")[0]
            address[i["address_type"]] = i

        htmlData["account_number"] = htmlData["account"]["bankaccount"][0][
            "account_number"
        ]

        htmlData["documents"] = documents
        htmlData["bankaccounts"] = bankaccounts
        htmlData["address"] = address

        htmlData[
            "p_address"
        ] = f"{address['PERMANENT']['building_name']}  {address['PERMANENT']['street_name']}  {address['PERMANENT']['city']}  {address['PERMANENT']['state']}  {address['PERMANENT']['pincode']} {address['PERMANENT']['country']} "

        htmlData[
            "c_address"
        ] = f"{address['CORRESPONDENCE']['building_name']}  {address['CORRESPONDENCE']['street_name']}  {address['CORRESPONDENCE']['city']}  {address['CORRESPONDENCE']['state']}  {address['CORRESPONDENCE']['pincode']} {address['CORRESPONDENCE']['country']} "

        htmlData[
            "p_residential_ownership"
        ] = f"{address['PERMANENT']['residential_ownership']}"

        htmlData[
            "c_residential_ownership"
        ] = f"{address['CORRESPONDENCE']['residential_ownership']}"


        for k, v in htmlData["product"].items():
            htmlData["product__" + k] = v
        for k, v in htmlData["product"]["lender"].items():
            htmlData["product__lender__" + k] = v


        htmlData["logo_path"] = settings.LOGO


        htmlData[
            "emi_schedule"
        ] = ApplicationService().generate_application_amort_schedule(
            app_id=application.application_id
        )


        template = get_template("application/index.html")

        # data is the context data that is sent to the html file to render the output.
        asset_dict = {}
        for i,a in enumerate(htmlData['asset']):
            asset_dict[i+1] = dict(a)
        htmlData['asset'] = asset_dict

        htmlData['packet_id']=''
        htmlData['referral_code']=''
        html = template.render(htmlData)

        options = {
            "page-size": "A4",
            "margin-top": "5mm",
            "margin-right": "5mm",
            "margin-bottom": "5mm",
            "margin-left": "5mm",
            "enable-local-file-access": "",
            "encoding": "UTF-8",
        }

        pdf = pdfkit.from_string(html, False,options=options, configuration=pdfkit.configuration())

        return pdf
