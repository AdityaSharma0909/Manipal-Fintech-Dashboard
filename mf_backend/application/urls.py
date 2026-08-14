from django.urls import path
from .views.ApplicationView import (
    ApplicationViewAPI,
    AmortizationView,
    UpdateApplicationProductView,
)
from .views.ApplicationOverview import ApplicationOverviewView
from .views.GoldDeposit import GoldDepositOtpGenerator, GoldDepositOtpVerify
from .views.LoanAmount import LoanAmountView, GoodsView
from .views.AppplicationConfirmation import (
    ApplicationConfirm,
    LoanDocumentVerification,
    ApplicationConfirmationCPC,
)
from .search import ApplicationSearchAPI
from .views.application_sent_back_to_cpc import ApplicationRevertToCPCView
from .views.esign_application import EsignApplicationView
from .views.goldCollection import GoldCollectionOtpGenerator, GoldCollectionOtpVerify
from .views.export_application_data import ExportApplicationView
# from .views.export_user_data import ExportUserApplicationView
from .views.jewellery_types import JewelleryView
from .views.loanDocView import TakeOverDocView , UnsecuredLoanDocView
from .views.mail_export_reports import MailReportView
from .views.pending_applications import PendingApplicationView
from .views.Application_history import ApplicationHistoryView
from .views.Meta_Field_Check import MetaCheckerView
from .views.cam_report import ExportCamView
from .views.generate_pdf import Generate_pdf
from .views.application_document import ApplicationDocumentView
from .views.unsecured_loan_document import UnsecuredLoanDocument , UnsecuredLoanEsignView
from .views.sanction_document import SanctionDocument , SanctionEsignView
from .views.dpn_document import DpnDocument , DpnEsignView
from .views.reassign_application import ReassignApplication
from .views.export_insurance_MU import ExportMUInsuranceView
from .views.NewApplicationView import NewApplicationView


urlpatterns = [
    path("", ApplicationViewAPI.as_view()),
    path("update_product/", UpdateApplicationProductView.as_view()),
    path("overview/", ApplicationOverviewView.as_view()),
    path("add-loanamount/", LoanAmountView.as_view()),
    path("getApplicationAmzSchedule/", AmortizationView.as_view()),
    path("confirmation/", ApplicationConfirm.as_view()),
    path("loan-document/", LoanDocumentVerification.as_view()),
    path("loan-document/confirm/", ApplicationConfirmationCPC.as_view()),

    path("gold-deposit/generate/", GoldDepositOtpGenerator.as_view()),
    path("gold-deposit/verify/", GoldDepositOtpVerify.as_view()),

    path("gold-collection/generate/", GoldCollectionOtpGenerator.as_view()),
    path("gold-collection/verify/", GoldCollectionOtpVerify.as_view()),

    path("add-goods/", GoodsView.as_view()),
    path("export/", ExportApplicationView.as_view()),
    # path("export_user/", ExportUserApplicationView.as_view()),
    path('all_jewellery_type', JewelleryView.as_view()),
    path('esign-request', EsignApplicationView().as_view()),
    path('rollback-to-cpc', ApplicationRevertToCPCView.as_view()),
    path('doc/takeover', TakeOverDocView.as_view()),
    path('search/', ApplicationSearchAPI.as_view()),
    path('pending/', PendingApplicationView.as_view()),
    path('report/mail',MailReportView.as_view()),
    path('history/',ApplicationHistoryView.as_view()),
    path('meta_checker/', MetaCheckerView.as_view()),
    path('cam-report/', ExportCamView.as_view()),
    path('template/html_to_pdf/',Generate_pdf.as_view()),
    path('upload_doc/',ApplicationDocumentView.as_view()),
    path('unsecured/',UnsecuredLoanDocument.as_view()),
    path('sanction/',SanctionDocument.as_view()),
    path('dpn/',DpnDocument.as_view()),
    path('esign-unsecured/',UnsecuredLoanEsignView.as_view()),
    path('esign-sanction/',SanctionEsignView.as_view()),
    path('esign-dpn/',DpnEsignView.as_view()),
    path('loan-doc/',UnsecuredLoanDocView.as_view()),
    path('reassign/',ReassignApplication.as_view()),
    path('export-insurance',ExportMUInsuranceView.as_view()),
    path('new-application/', NewApplicationView.as_view()),

]
