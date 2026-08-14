from django.urls import path

from .views.bt_inspection_docs import BtInspectionDocView
from .views.interest_accrual_penalty import CalculateLoanView
from .views.loan import LoanView,LoanAllView,LoanAssetView
from .views.LoanEMI import LoanEMIView ,LoanEMIRecordView
from .views.loan_payment_transaction import LoanPaymentTransactionView
from .views.loan_take_over import LoanTakeOverView
from .views.manual_dpd import ManualPenaltyView
from .views.manual_interest_accrual import ManualInterestAccrualView
from  .services.other_lender_appraisal import OtherLenderAppraisalView
from .views.export_loan_data import ExportLoanView
from .views.takeover_residence_view import LoanTakeOverResidenceView
from .views.loan_bill_generation import LoanBillAPIView
from .search import LoanSearchAPI
from .views.Loan_history import LoanHistoryView


urlpatterns =[
    path("",LoanView.as_view()),
    path("all/",LoanAllView.as_view()),
    path("emi/",LoanEMIView.as_view()),
    path("emi/record/",LoanEMIRecordView.as_view()),
    # path("collect/generate/",CollectGoldOtpView.as_view()),
    # path("collect/verify/",VerifyOtpView.as_view())
    path('takeover', LoanTakeOverView.as_view()),
    path('payment', LoanPaymentTransactionView.as_view()),
    path('accrue-interest-manual', ManualInterestAccrualView.as_view()),
    path('dpd-penalty',ManualPenaltyView.as_view()),
    path('other_lender_appraisal', OtherLenderAppraisalView.as_view()),
    path("export/", ExportLoanView.as_view()),
    path("manual/check/payoffs", CalculateLoanView.as_view()),
    path('takeover/residence',LoanTakeOverResidenceView.as_view()),
    path('takeover/residence/docs', BtInspectionDocView.as_view()),
    path('generate/',LoanBillAPIView.as_view()),
    path('search/', LoanSearchAPI.as_view()),
    path('loan-asset/', LoanAssetView.as_view()),
    path('history/',LoanHistoryView.as_view()),
]