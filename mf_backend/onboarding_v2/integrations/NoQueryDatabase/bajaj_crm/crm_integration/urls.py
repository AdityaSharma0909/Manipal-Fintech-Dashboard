from django.urls import path
from crm_integration.views import BajajFinServoLeadCreateView, MasterBranchView, TokenTestView

urlpatterns = [
    # Leads Controller Create endpoint
    path('leads/Create', BajajFinServoLeadCreateView.as_view(), name='bajaj-lead-create'),
    
    # Master Controller Branch endpoint
    path('master/branch', MasterBranchView.as_view(), name='bajaj-master-branch'),

    # Token test endpoint - standalone token generation test
    path('test-token', TokenTestView.as_view(), name='bajaj-test-token'),
]
