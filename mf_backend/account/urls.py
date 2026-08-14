"""All account related endpionts goes here"""

from django.urls import path
from .views.account import CustomerAccount , AgentAccountAPIView, AgentOnboardingStatusAPIView
from .views.BankAccount import BankAccountAPI , AgentBankAccountView
from .views.CustomerOverview import CustomerOverviewView ,AllAplications
from .views.Nominee import NomineeDetailsView , WellnessNomineeView
from .views.account_verification import AccountVerificationView
from .views.insurance_view import InsuranceView , InsuranceAllView
from .views.sprint_verify_docs import SprintVerifyDocsView
from .views.update_gprs import UpdateGprsDataView
from .views.verify_docs import VerifyDocView
from .views.export_insurance_data import ExportInsuranceView
from .search import AccountSearchAPI
from .views.export_account_data import ExportAccountView
from .views.Account_history import AccountHistoryView
from .views.reassign_account import ReassignAccount
from .views.NewAccountView import NewAccountView

urlpatterns = [
    path('customer/',CustomerAccount.as_view()),
    path('bankaccount/',BankAccountAPI.as_view()),
    path('overview/',CustomerOverviewView.as_view()),
    path('nominee/',NomineeDetailsView.as_view()),
    path('all/',AllAplications.as_view()),
    path('verify', VerifyDocView.as_view()),
    path('customer/kyc-update',AccountVerificationView.as_view()),
    path('insurance/export/',ExportInsuranceView.as_view()),
    path('insurance', InsuranceView.as_view()),
    path('search/',AccountSearchAPI.as_view()),
    path('export/',ExportAccountView.as_view()),
    path('verify/<str:verification_type>/',SprintVerifyDocsView.as_view()),
    path('history/',AccountHistoryView.as_view()),
    path('geo-images', UpdateGprsDataView.as_view()),
    path('reassign', ReassignAccount.as_view()),
    path('insurance/all', InsuranceAllView.as_view()),
    path('nominee/wellness',WellnessNomineeView.as_view()),
    path('agent/',AgentAccountAPIView.as_view()),
    path('agent/onboarding-status/',AgentOnboardingStatusAPIView.as_view()),
    path('agent/bankaccount/',AgentBankAccountView.as_view()),
    path('new-account/', NewAccountView.as_view()),
]
