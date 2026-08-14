# flow/urls.py
from django.urls import path
from .views import FlowView

urlpatterns = [
    path('', FlowView.as_view(), name='flowView'),
]
