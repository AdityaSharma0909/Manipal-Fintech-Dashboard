from django.urls import path
from .views.reference_pd import ReferencePDView

urlpatterns = [
    path("", ReferencePDView.as_view()),
]
