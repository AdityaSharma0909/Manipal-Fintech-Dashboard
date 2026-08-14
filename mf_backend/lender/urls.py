from django.urls import path
from .views.lender import LenderView

urlpatterns = [
    path("",LenderView.as_view()),
  
]
