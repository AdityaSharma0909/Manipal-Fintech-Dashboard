from django.urls import path 
from .views.DocumentView import DocumentView

urlpatterns =[
    path("",DocumentView.as_view()),
    
]