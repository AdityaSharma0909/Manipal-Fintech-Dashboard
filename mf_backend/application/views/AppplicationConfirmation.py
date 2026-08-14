from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.views import APIView
import numpy_financial as npf
from django.template.loader import get_template
import os
from dateutil.relativedelta import relativedelta
import pdfkit
from application.service import ApplicationService
from ..models import Application
from utils.responseHandler import HttpResponse
from django.http import HttpResponse as HttpResponseBase
from utils.constants import APPROVED, REJECTED, APPLICATION_STATUS, ROLES
from loan.models import Loan, LoanEMISchedule
# from ..LoanDocumentService import render_to_pdf
from utils.constants import APPLICATION_STATUS 
from document.serializers import LoanDocumentSerializer
from application.models import LoanDocument
from document.utils.document_utils import DocumentUtils
from ..serializers import ApplicationOverviewSerializer
from disbursements.models import Disbursement
from django.conf import settings
import utils.helper as helper
from ..services.application_services import ApplicationHelper
from rest_framework.permissions import IsAuthenticated

class ApplicationConfirm(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        # Retrieve the current user from the request
        user = request.user

        # Get necessary data from the request
        application_id = request.data.get("application_id", None)
        response = request.data.get("response", None)
        comment = request.data.get("comment", None)
        rejection_status = request.data.get('rejection_status', None)

        def approve_application(**kwargs):
            return ApplicationHelper().approve_application(
                approved_by=request.user,
                response=response,
                comment=comment,
                application_id=application_id,
                rejection_status=rejection_status,
                **kwargs
            )

        # Check if the user's role is CPC
        if user.role == ROLES.CPC.value:
            # Ensure 'response' and 'application_id' are provided, return a bad request response if not
            if not response or not application_id:
                return HttpResponse.BadRequest(
                    "'response' and 'application_id' are required"
                )
            
            return approve_application()

        # Check if the user's role is Credit Manager
        elif user.role == ROLES.CREDIT_MANAGER.value:
            # Get 'loan_amount' from the request data
            loan_amount = request.data.get('loan_amount', None)

            # Ensure 'response', 'application_id', and 'loan_amount' are provided, return a bad request response if not
            if not response or not application_id or (response != 'ROLL_BACK' and loan_amount is None):
                return HttpResponse.BadRequest(
                    "'response', 'application_id' and 'loan_amount' are required"
                )
            
            # Get 'deviated_amount' from the request data if the response is 'DEVIATE'
            deviated_amount = request.data.get('deviated_amount', None) if response == 'DEVIATE' else None

            # Ensure 'deviated_amount' is provided if the response is 'DEVIATE', return a bad request response if not
            if response == 'DEVIATE' and deviated_amount is None:
                return HttpResponse.BadRequest(
                    "deviated_amount is required "
                )
            
            return approve_application(loan_amount=loan_amount, deviated_amount=deviated_amount)

        # Check if the user's role is Business Head
        elif user.role == ROLES.BUSINESS_HEAD.value:
            # Ensure 'response' and 'application_id' are provided, return a bad request response if not
            if not response or not application_id:
                return HttpResponse.BadRequest(
                    "'response' and 'application_id' are required"
                )
            
            loan_amount = request.data.get('loan_amount', None)
            deviated_amount = request.data.get('deviated_amount', None)

            return approve_application(loan_amount=loan_amount, deviated_amount=deviated_amount)

        # Return a bad request response if the user's role is invalid
        else:
            return HttpResponse.BadRequest("Invalid user role")


    def get(self, request):
        if request.user.role != ROLES.CPC.value:
            return HttpResponse.Unauthorized({"error": "Only CPC is allowed "})
        application = Application.objects.get(
            application_id=request.GET.get("application_id")
        )

        document = LoanDocument.objects.get(application=str(application.application_id))
        # response = request.data["response"]
        # Loan.objects.create(
        #     loan_number=application.application_number,
        #     application=application,
        #     status="Loan created",
        #     term="Term",
        #     intrest_rate=application.product.intrest_rate,
        #     loan_amount=application.loan_amount,
        #     loan_type=application.product.product_type,
        #     days_past_dues=application.product.tenure,
        #     current_amount=application.loan_amount
        #     ).save()

        # if response =="True":
        #     return HttpResponse.Success({"success":"Your loan is Disbursed"})
        document_serialized = LoanDocumentSerializer(document)
        return HttpResponse.Success({"success": document_serialized.data})


# class ApplicationConfirmCPC(APIView):
#     def post(self, request, *args, **kwargs):
#         if request.user.role != ROLES.CPC.value:
#             return HttpResponse.Unauthorized({"error": "Only CPC is allowed "})
#         application = Application.objects.get(application_id=request.data['application_id'])

#         response=request.data["response"]

#         if application.status==APPLICATION_STATUS.APPLICATION_SENT_TO_CPC.value:

#             if response==APPROVED:
#                 application.status=APPLICATION_STATUS.APPLICATION_COMPLETED.value
#                 application.approvedByCPC=User.objects.get(user_id=request.user.user_id)
#                 application.save()

#                 # TODO we need  to create loan document and send loan document in response.

#                 # Loan.objects.create(
#                 #     loan_number=application.application_number,
#                 #     application=application,
#                 #     status="Loan created",
#                 #     term="Term",
#                 #     intrest_rate=application.product.intrest_rate,
#                 #     loan_amount=application.loan_amount,
#                 #     loan_type=application.product.product_type,
#                 #     days_past_dues=application.product.tenure,
#                 #     current_amount=application.loan_amount
#                 #     ).save()


#                 return HttpResponse.Success({"success":"Your application approved by CPC."})
#             elif response==REJECTED:
#                 application.status=APPLICATION_STATUS.APPLICATION_REJECTED_BY_CPC.value
#                 application.save()
#                 return HttpResponse.Success({"sucess": "Your application is rejected by CPC"})
#         else:
#             HttpResponse.BadRequest({"error": "Your application must be approved by the Branch Manager"})

#         return HttpResponse.BadRequest({"error":"No response was received"})


#         # on the basis of application id we need to generate loan document


#         # if application.status==APPLICATION_STATUS.APPLICATION_SENT_TO_CPC.value:

#         #     if response==APPROVED:
#         #         application.status=APPLICATION_STATUS.APPLICATION_COMPLETED.value
#         #         application.save()


#         #         # Loan.objects.create(
#         #         #     loan_number=application.application_number,
#         #         #     application=application,
#         #         #     status="Loan created",
#         #         #     term="Term",
#         #         #     intrest_rate=application.product.intrest_rate,
#         #         #     loan_amount=application.loan_amount,
#         #         #     loan_type=application.product.product_type,
#         #         #     days_past_dues=application.product.tenure,
#         #         #     current_amount=application.loan_amount
#         #         #     ).save()


#         #     elif response==REJECTED:
#         #         application.status=APPLICATION_STATUS.APPLICATION_REJECTED_BY_CPC.value
#         #         application.save()
#         #         return HttpResponse.Success({"sucess": "Your application is rejected by CPC"})
#         # else:
#         #     HttpResponse.BadRequest({"error": "Your application must be approved by the Branch Manager"})

#         # return HttpResponse.BadRequest({"error":"No response was received"})


def read_text_from_file(file_path):
    with open(file_path, encoding="utf8", errors="ignore") as f:
        text = f.read()
        return text


class LoanDocumentVerification(APIView):
    def get(self, request):
        # print(" :::::::::::::::::::: Generating Loan Doc ::::::::::::::::::;;;")
        # s = datetime.datetime.now()
        # print(s)
        application = Application.objects.get(
            application_id=request.GET.get("application_id")
        )
        # print(application.status)
        applicationData = ApplicationOverviewSerializer(application)

        # data = {
        # "application_number": application.application_number, #you can feach the data from database

        # "date":application.created_at.strftime("%d-%m-%Y"),
        # "customer_name":application.account.user.first_name+" "+application.account.user.last_name,

        # }
        htmlData = applicationData.data
        # htmlData["base_dir"] = settings.BASE_DIR
        # htmlData["media_base_url"] = environment.BASE_URL

        if htmlData["goods"]:
            # for k, v in htmlData["goods"].items():
            goodsMap = {}
            for good in htmlData["goods"]:
                good["total_price"] = round(good["quantity"] * good["goods_price"], 2)
                goodsMap["goods__" + good["goods_id"]] = dict(good)
            htmlData["goods"] = goodsMap
        else:
            htmlData["goods"] = {}

        for k, v in htmlData["account"].items():
            htmlData["account__" + k] = v

        # htmlData["Subtotal"] = 0

        # for i in htmlData["asset"]:
        #     htmlData["Subtotal"] = float(i["asset_price"]) + float(htmlData["Subtotal"])

        # htmlData["ProcessingFee"] = float(htmlData["Subtotal"]) * (
        #     float(htmlData["product"]["processing_fee"]) / 100
        # )
        # htmlData["Gst"] = float(htmlData["ProcessingFee"]) * 0.18
        # htmlData["Total"] = (
        #     float(htmlData["Subtotal"])
        #     - float(htmlData["Gst"])
        #     - float(htmlData["ProcessingFee"])
        # )

        # htmlData["Subtotal"] = round(htmlData["Subtotal"], 2)
        # htmlData["Gst"] = round(htmlData["Gst"], 2)
        # htmlData["ProcessingFee"] = round(htmlData["ProcessingFee"], 2)
        # htmlData["Total"] = round(htmlData["Total"], 2)

        htmlData["account__created_at"] = ApplicationService().format_date(
            htmlData["account__created_at"].split("T")[0]
        )
        htmlData["account__year_of_birth"] = ApplicationService().format_date(
            htmlData["account__year_of_birth"].split("T")[0]
        )
        # htmlData["account__caste"] = htmlData["account__caste"].lower()
        htmlData["account__gender"] = htmlData["account__gender"].lower()

        # htmlData["profile_picture"]="http://101.53.135.26:8000"+htmlData["account"]["profile_photo"]["file"]

        profilePath = os.path.join(
            settings.MEDIA_ROOT, htmlData["account"]["profile_photo"]["file_name"]
        )
        # print(profilePath)
        # with open(profilePath, "rb") as image_file:
        #     encoded_string = base64.b64encode(image_file.read())
        #     htmlData["profile_picture"]=encoded_string.decode('utf-8')

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
        # print(documents)
        for k, v in documents.items():
            #v["file"] = "http://101.53.135.26:8000" + v["file"]
            v["file"] = "http://127.0.0.1:8001" + v["file"]
        # print(documents)
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

        # print(address)

        for k, v in htmlData["product"].items():
            htmlData["product__" + k] = v
        for k, v in htmlData["product"]["lender"].items():
            htmlData["product__lender__" + k] = v

        # print("logo:::: ")
        # print(settings.LOGO)
        # with open(settings.LOGO, "rb") as lf:
        #     encoded_string = base64.b64encode(lf.read())
        #     htmlData["logo"]=encoded_string.decode('utf-8')
        htmlData["logo_path"] = settings.LOGO

        # print(
        #     " :::::::::::::::::::: Loan Doc: Query Finished for ::::::::::::::::::;;;"
        # )
        # e = datetime.datetime.now()
        # print(e)
        # print(e - s)

        htmlData[
            "emi_schedule"
        ] = ApplicationService().generate_application_amort_schedule(
            app_id=request.GET.get("application_id")
        )

        # print(" :::::::::::::::::::: Loan Doc: EMI calculated ::::::::::::::::::;;;")
        # e = datetime.datetime.now()
        # print(e)
        # print(e - s)

        # print("emi schedule ================",htmlData)
        # pdf = render_to_pdf(htmlData)
        # print("pdf------------------", pdf)
        # if pdf:
        #     response = HttpResponseBase(pdf, content_type="application/pdf")
        #     filename = "Report_for_%s.pdf" % (
        #         applicationData.data["application_number"]
        #     )
        #     content = "inline; filename= %s" % (filename)
        #     response["Content-Disposition"] = content
        #     return response

        # return HttpResponseBase("Page Not Found")
        template = get_template("application/index.html")

        # data is the context data that is sent to the html file to render the output.
        asset_dict = {}
        for i,a in enumerate(htmlData['asset']):
            asset_dict[i+1] = dict(a)
        htmlData['asset'] = asset_dict
        htmlData['packet_id']='12324'
        htmlData['referral_code']='refecasd'
        # print(json.dumps(htmlData, indent=4, default=str, sort_keys=True))
        html = template.render(htmlData)

        # print(
        #     " :::::::::::::::::::: Loan Doc: HTML data rendered ::::::::::::::::::;;;"
        # )
        # e = datetime.datetime.now()
        # print(e)
        # print(e - s)

        wkhtmltopdf = "C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"

        # Renders the template with the context data.
        options = {
            "page-size": "A4",
            "margin-top": "5mm",
            "margin-right": "5mm",
            "margin-bottom": "5mm",
            "margin-left": "5mm",
            "enable-local-file-access": "",
            # "header-center": "YOUR HEADER",
            # "custom-header": [("Accept-Encoding", "gzip")],
            # "no-outline": None,
            "encoding": "UTF-8",
            # 'header-left'  : 'something',
            # 'header-right' : '[section]',
            # 'footer-left': "This is a footer",
            # 'footer-font-size':'70',
            # 'footer-font-name':'#ffffff',
            # 'footer-right': '[page] of [topage]',
            # "footer-html": "footer.html",
            # "custom-header": [("Accept-Encoding", "gzip")],
            # "no-outline": None,
        }

        pdf = pdfkit.from_string(html, False,options=options, configuration=pdfkit.configuration())
        # pdf = pdfkit.from_string(html, False,options=options, configuration=pdfkit.configuration(wkhtmltopdf=wkhtmltopdf))
        # pdf = pdfkit.from_string(
        #     html,
        #     False,
        #     options=options,
        #     configuration=pdfkit.configuration(),
        #     verbose=True,
        # )
        response = HttpResponseBase(content_type="application/pdf")
        filename = "{app_no}-{fn}_{ln}.pdf".format(
            app_no=application.application_number,
            fn=htmlData["account__user__first_name"],
            ln=htmlData["account__user__last_name"],
        )
        response["Content-Disposition"] = 'attachment; filename="{filename}"'.format(
            filename=filename
        )
        response["Access-Control-Expose-Headers"] = 'Content-Disposition'
        response.write(pdf)
        # e = datetime.datetime.now()
        # print(e)
        # print(e - s)
        return response

        # return HttpResponseBase(,content_type="application/pdf")

    def post(self, request, *args, **kwargs):
        try:
            user = request.user

            # if request.user.role != ROLES.LOAN_OFFICER.value:
            #      return HttpResponse.Unauthorized({"error": "Only Loan officer is allowed "})
            loan_documents = request.FILES.getlist("document",[])

            print(loan_documents)

            application = Application.objects.get(
                application_id=request.data["application_id"]
            )
            service = DocumentUtils(request.user)
            resp=[]
            for loan_document in loan_documents:
                loan_document_size = loan_document.size / (1024 * 1024)
                if loan_document_size >= 10:
                    return HttpResponse.Success({'msg': 'Please choose a file below 10MB'})

                document_serialized = service.upload_loan_document_new(
                    file=loan_document, application=str(application.application_id),
                    document_type=request.data.get('document_type')
                )

                if document_serialized.is_valid():

                    data=document_serialized.save()
                    resp.append(LoanDocumentSerializer(data).data)

                else:
                    resp = HttpResponse.BadRequest({"errors": document_serialized.errors})
                    return resp
            verify_if_all_doc_posted = service.verify_all_takeover_loan_documents(
                application_id=application.application_id)

            if verify_if_all_doc_posted and application.status in [APPLICATION_STATUS.TAKE_OVER_LOAN_INITIATED.value,
                                                                   APPLICATION_STATUS.BT_NOMINEE_ADDED.value,
                                                                   APPLICATION_STATUS.BT_RESIDENCE_ADDED.value]:
                application.status = APPLICATION_STATUS.TAKE_OVER.value
            application.save()
            resp = HttpResponse.Success({"loan_document": resp})
            return resp


        except IntegrityError:
            return HttpResponse.BadRequest({'error':f'Document with document_type {request.data.get("document_type")} already exist'})
        except Exception as e:
            return HttpResponse.InternalServerError({'error':str(e)})


    def patch(self, request):
        try:
            document_id=request.data.get('document_id')
            loan_document=request.data.get('document')
            content_file = ContentFile(loan_document.read())
            document=LoanDocument.objects.get(document_id=document_id)
            document.file_name = loan_document.file_name
            document.file.save(loan_document.file_name,content_file, save=True)
            document.save()
            return HttpResponse.Success({"loan_document": [LoanDocumentSerializer(loan_document).data]})
        except ObjectDoesNotExist:
            return Response({'error':'Loan document not found'}, status=404)
        except Exception as e:
            return HttpResponse.InternalServerError(errorMsg={'error':str(e)})

    def delete(self, request):
        try:
            document_id=request.data.get('document_id')
            document=LoanDocument.objects.get(document_id=document_id)
            document.delete()
            return HttpResponse.Success({"msg": 'Deleted document successfully'})
        except ObjectDoesNotExist:
            return Response({'error':'Loan document not found'}, status=404)
        except Exception as e:
            return HttpResponse.InternalServerError(errorMsg={'error':str(e)})


class ApplicationConfirmationCPC(APIView):
    def post(self, request, *args, **kwargs):
        if request.user.role != ROLES.CPC.value:
            return HttpResponse.Unauthorized({"error": "Only CPC is allowed "})
        application = Application.objects.get(
            application_id=request.data["application_id"]
        )
        response = request.data["response"]

        user = request.user

        if user.role == ROLES.CPC.value and application.status == APPLICATION_STATUS.APPLICATION_INITIATED.value:
            if response == APPROVED:
                # Loan.objects.create(
                #     loan_number=application.application_number,
                #     application=application,
                #     status=LOAN_STATUS.NEW.value,
                #     term=application.product.tenure,
                #     intrest_rate=application.product.interest_rate,
                #     loan_amount=application.loan_amount,
                #     loan_type=application.product.product_type,
                #     days_past_dues=application.product.tenure,
                #     current_amount=application.loan_amount,
                #     processing_fee=application.processing_fee,
                #     stamp_duty=application.stamp_duty,
                #     penalty=application.penalty,
                #     ltv=application.ltv,
                #     tenure=application.tenure,
                #     lender=application.lender,
                #     purpose_of_loan=application.purpose_of_loan,
                #     eligible_amount=application.eligible_amount,
                #     product=application.product,
                #     total_goods_price=application.total_goods_price,
                #     total_weight=application.total_weight,
                #     net_weight=application.net_weight,
                #     period=application.period,
                #     Originatedby=application.Originatedby,
                #     appraisedBy=application.appraisedBy,
                #     approvedByBM=application.approvedByBM,
                #     approvedByBMAt=application.approvedByBMAt,
                #     approvedByCPC=application.approvedByCPC,
                #     approvedByCPCAt=application.approvedByCPCAt,
                    
                #     current_gst_rate =application.current_gst_rate,
                #     gst=application.gst,
                    
                   
                    
                #     gold_rate_per_gram=application.gold_rate_per_gram,
                #     lending_gold_rate_per_gram=application.lending_gold_rate_per_gram,
                   
                #     disbursed_amount=application.disbursed_amount,
                #     disbursed_date=application.disbursed_date,
                #     due_date=application.due_date,
                #     disbursal_amount =application.disbursal_amount ,
                #     net_disbursed_amount=application.net_disbursed_amount
                # ).save()

                if application.total_goods_price:
                    Disbursement.objects.create(
                        loan=Loan.objects.get(application=application),
                        disbursement_amount=helper.get_disbursement_amount(
                            loan_amount=float(application.loan_amount),
                            processing_fee=float(application.product.processing_fee),
                            stamp_duty=float(application.stamp_duty),
                        )
                        - float(application.total_goods_price),
                    ).save()

                    loan = Loan.objects.filter(application=application).first()
                    disbursement = Disbursement.objects.get(loan=loan)
                    application.disbursed_date = disbursement.disbursal_date
                    due_date = disbursement.disbursal_date + relativedelta(
                        months=loan.tenure
                    )

                    application.due_date = due_date
                    application.status = APPLICATION_STATUS.LOAN_DISBURSED.value
                    application.net_disbursed_amount = helper.get_disbursement_amount(
                        loan_amount=float(application.loan_amount),
                        processing_fee=float(application.product.processing_fee),
                        stamp_duty=float(application.stamp_duty),
                    ) - float(application.total_goods_price)
                    application.save()
                    
                    LoanEMISchedule.objects.create(
                        application=application,
                        loan=Loan.objects.get(application=application),
                        principal=application.net_disbursed_amount,
                        apr=application.intrest_rate,
                        term=application.tenure,
                        emi_amount=npf.pmt(
                            application.intrest_rate / 12,
                            application.tenure,
                            application.net_disbursed_amount,
                        ),
                    )

                else:
                    Disbursement.objects.create(
                        loan=Loan.objects.get(application=application),
                        disbursement_amount=helper.get_disbursement_amount(
                            loan_amount=float(application.loan_amount),
                            processing_fee=float(application.product.processing_fee),
                            stamp_duty=float(application.stamp_duty),
                        ),
                    ).save()

                    loan = Loan.objects.filter(application=application).first()
                    disbursement = Disbursement.objects.get(loan=loan)
                    application.disbursed_date = disbursement.disbursal_date
                    due_date = disbursement.disbursal_date + relativedelta(
                        months=loan.tenure
                    )
                    application.due_date = due_date
                    application.net_disbursed_amount = application.disbursed_amount
                    application.save()
                    application.status = APPLICATION_STATUS.LOAN_DISBURSED.value
                    application.save()
                    LoanEMISchedule.objects.create(
                        application=application,
                        loan=Loan.objects.get(application=application),
                        principal=application.net_disbursed_amount,
                        apr=application.intrest_rate,
                        term=application.tenure,
                        emi_amount=npf.pmt(
                            application.intrest_rate / 12,
                            application.tenure,
                            application.net_disbursed_amount,
                        ),
                    )
                
                # FCMService([application.Originatedby]).generateNotification(
                #     title="Loan Status", message=" Your Loan is Generated "
                # )
                return HttpResponse.Success({"success": "Your loan is Generated"})
            elif response == REJECTED:

                # FCMService([application.Originatedby]).generateNotification(
                #     title="Loan Status", message=" Your Loan is Rejected "
                # )
                return HttpResponse.Success({"error": "Your loan is Rejected"})
        else:
            return HttpResponse.Forbidden()

    def get(self, request):
        if request.user.role != ROLES.CPC.value:
            return HttpResponse.Unauthorized({"error": "Only CPC is allowed "})
        application = Application.objects.get(
            application_id=request.GET.get("application_id")
        )

        loan_document = LoanDocument.objects.filter(application=application).first()

        ser = LoanDocumentSerializer(loan_document)

        return HttpResponse.Success({"loan_document": ser.data})
