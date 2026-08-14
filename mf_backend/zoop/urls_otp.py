from django.urls import path
from .views_otp import SendOTPView, ResendOTPView, VerifyOTPView

urlpatterns = [
    path("send-otp/", SendOTPView.as_view()),
    path("resend-otp/", ResendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
]
