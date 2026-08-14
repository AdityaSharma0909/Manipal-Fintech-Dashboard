

from django.urls import path

from core.views.create_application_third_party import CreateApplicationView
from core.views.customer_dashboard_view import CustomerDashboardView, CustomerApplicationDetailsView
from core.views.frs_callback import FrsCallbackView, UpdateFrsCallbackManully
from core.views.login_third_party import LoginThirdPartyView
from core.views.register_accounts_third_party import RegisterThirdPartyAccountsView
from core.views.register_third_party import RegisterThirdPartyView
from core.views.sql_backup_manual import UploadBackup
from core.views.test_axis_calls import TestAxisBankView
from core.views.third_party_loan_doc import ThirdPartyLoanDoc
from core.views.upload_sql import UploadDocs
from core.views.verify_kyc import VerifyKycView
from core.views.gov_pincode import GetGovPincode
from core.views.india_locations import IndiaStatesDistrictsSlashView, IndiaStatesDistrictsView

urlpatterns = [
    path('upload-file',UploadDocs.as_view()),
    path('frs/callback',FrsCallbackView.as_view()),
    path('manual/frs/callback',UpdateFrsCallbackManully.as_view()),
    path('login', LoginThirdPartyView.as_view()),
    path('register', RegisterThirdPartyView.as_view()),
    path('account', RegisterThirdPartyAccountsView.as_view()),
    path('account/verify',VerifyKycView.as_view()),
    path('application',CreateApplicationView.as_view()),
    path('application/document',ThirdPartyLoanDoc.as_view()),
    path('customer/dashboard', CustomerDashboardView.as_view()),
    path('customer/dashboard/application', CustomerApplicationDetailsView.as_view()),
    path('test/axis/<str:endpoint>', TestAxisBankView.as_view()),

    path('gov/pincode', GetGovPincode.as_view()),
    path('india/states-districts', IndiaStatesDistrictsView.as_view()),
    path('india/states-districts/', IndiaStatesDistrictsSlashView.as_view()),
]
