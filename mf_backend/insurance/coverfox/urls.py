from django.urls import path

from insurance.coverfox.views.coverfox import CoverFoxView
from insurance.coverfox.views.medibuddy import MediBuddyView

urlpatterns = [
    path('coverfox/', CoverFoxView.as_view(), name="coverfox"),
    path('medibuddy/', MediBuddyView.as_view(), name="medibuddy"),
]