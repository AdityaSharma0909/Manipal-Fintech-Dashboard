"""All user & auth related endpionts goes here"""

from django.urls import path

from .views.all_branches import AllBranchesView
from .views.branch import BranchView, BranchDetailsView
from .views.export_branch_data import ExportBranchView


urlpatterns = [
    # path('', LoginView.as_view(), name='login'),
    path('', BranchView.as_view()),
    path('branchDetails/', BranchDetailsView.as_view()),
    path('data',AllBranchesView.as_view()),
    path('export/',ExportBranchView.as_view())
  
    # path(r"notification/", FCMNotificationView.as_view()),
]
