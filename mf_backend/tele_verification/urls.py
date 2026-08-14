from django.urls import path
from .views.tele_verification import TeleVerificationView
from .views.video_kyc import ForwardCustomerAPIView , CallDetailsAPIView ,FetchCustomerDetails


urlpatterns = [
    path("", TeleVerificationView.as_view()),
    path("applicant/forward/", ForwardCustomerAPIView.as_view(), name="forward-customer"),
    path("applicant/call-log/", CallDetailsAPIView.as_view(), name="call-log"),
    path("applicant/fetch-details/", FetchCustomerDetails.as_view(), name="fetch-customer"),
]
