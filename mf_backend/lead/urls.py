from django.urls import path 
from .views.LeadView import LeadView, LeadAllView, LeadDocumentView
from .views.DashboardView import LeadDashboard
from .search import LeadSearchAPI
from .views.axis_bank_call import AxisBankApiView
from .views.export_leads_data import ExportLeadView
from .views.LeadPhoneVerification import LeadOtpGenerationView, LeadOtpVerificationView
from .views.referedView import OpenReferedLeadView , ReferedLeadView
from .views.reassign_lead import AssignLeadView
from .views.NewLeadView import NewLeadView, UserNewLeadView, NewLeadDashboardView, MyNewLeadListView

urlpatterns =[
    path("dashboard/",LeadDashboard.as_view()),
    path("all/",LeadAllView.as_view()),
    path('search/', LeadSearchAPI.as_view()),
    path('export/',ExportLeadView.as_view()),
    path('generateOTP/', LeadOtpGenerationView.as_view()),
    path('verifyOTP/', LeadOtpVerificationView.as_view()),
    path("",LeadView.as_view()),
    path("axis", AxisBankApiView.as_view()),
    path("open-refer",OpenReferedLeadView.as_view()),
    path("refer",ReferedLeadView.as_view()),
    path("assign",AssignLeadView.as_view()),
    path('upload_doc/',LeadDocumentView.as_view()),
    path('new-lead/', NewLeadView.as_view()),
    path('new-lead-dashboard/', NewLeadDashboardView.as_view()),
    path('agent/new-lead/', MyNewLeadListView.as_view()),
]
