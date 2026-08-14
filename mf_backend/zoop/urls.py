from django.urls import path
from .views import (
    PanVerificationAPIView,BankVerificationView,
    DrivingLicenceVerificationView,ChequeOCRVerificationView,
    OCRLiteVerificationView,VoterIDAdvanceVerificationView,
    PassportAdvanceVerificationView,FaceMatchVerificationAPIView,
    SendOTPView,
    ResendOTPView,VerifyOTPView
    
)

urlpatterns = [
    path('verify-pan/', PanVerificationAPIView.as_view(), name='verify_pan'),
    path('verify-bank/', BankVerificationView.as_view(), name='bank-verification'),
    path('verify-driving-licence/', DrivingLicenceVerificationView.as_view(), name='verify-driving-licence'),
    path('cheque-ocr/verify/', ChequeOCRVerificationView.as_view(), name='cheque-ocr-verification'),
    path('ocr-lite/', OCRLiteVerificationView.as_view(), name='ocr-lite-verification'),
    path('voter/verify/', VoterIDAdvanceVerificationView.as_view(), name='voter-verify-verification'),
    path("passport/verify/", PassportAdvanceVerificationView.as_view(), name="passport-advance"),
    path("face-match/", FaceMatchVerificationAPIView.as_view(), name="face-match"),
    path("send-otp/", SendOTPView.as_view()),
    path("resend-otp/", ResendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),

] 
