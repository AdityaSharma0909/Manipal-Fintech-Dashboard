from django.urls import path

from .views import GoldPledgeCardResultView, GoldPledgeCardUploadView


urlpatterns = [
    path(
        "gold-pledge-card/",
        GoldPledgeCardUploadView.as_view(),
        name="gold-pledge-card-upload",
    ),
    path(
        "gold-pledge-card/result/",
        GoldPledgeCardResultView.as_view(),
        name="gold-pledge-card-result",
    ),
]

