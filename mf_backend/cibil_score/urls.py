from django.urls import path

from cibil_score.views.cibil_pull import CibilCreditPull
from cibil_score.views.idv_hra_pull import IdvHraPull
from cibil_score.views.upload_cam import UploadCibilScoreView
from cibil_score.views.cibil_score_view import CibilScoreView


urlpatterns = [
    path('credit-report',CibilCreditPull.as_view()),
    path('hra-report',IdvHraPull.as_view()),
    path('upload-cam', UploadCibilScoreView.as_view()),
    path('',CibilScoreView.as_view())
]