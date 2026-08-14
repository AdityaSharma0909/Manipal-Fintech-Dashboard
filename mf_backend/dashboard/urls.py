from django.urls import path
from dashboard.views import (
    LeadStatsView,
    ApplicationStatsView,
    LoanStatsView,
    TeamStatsView,
)

urlpatterns = [
    path("leads/",        LeadStatsView.as_view(),        name="dashboard-leads"),
    path("applications/", ApplicationStatsView.as_view(), name="dashboard-applications"),
    path("loans/",        LoanStatsView.as_view(),        name="dashboard-loans"),
    path("team/",         TeamStatsView.as_view(),        name="dashboard-team"),
]
