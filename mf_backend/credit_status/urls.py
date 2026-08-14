from django.urls import path 
from credit_status.views.CreditStatus import CreditStatusView

urlpatterns =[
    path("",CreditStatusView.as_view()),
]