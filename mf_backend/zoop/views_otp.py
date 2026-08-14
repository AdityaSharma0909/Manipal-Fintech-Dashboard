import random
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .otp_services import send_sms_otp

def validate_mobile(mobile):
    
    if not mobile or not mobile.isdigit():
        return False
    valid = len(mobile) == 10 or (len(mobile) == 12 and mobile.startswith("91"))
    return valid

class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile")
        
        if not validate_mobile(mobile):
            return Response({"success": False, "error": "Invalid mobile number"}, status=400)

        otp = random.randint(100000, 999999)

        cache.set(f"otp_{mobile}", otp, 300)

        try:
            send_sms_otp(mobile, otp)
        except Exception as e:
            return Response({
                "success": False,
                "error": "Failed to send OTP",
                "details": str(e)
            }, status=500)

        return Response({
            "success": True,
            "message": "OTP sent successfully",
            "mobile": mobile
        })

class ResendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile")

        if not validate_mobile(mobile):
            return Response({"success": False, "error": "Invalid mobile number"}, status=400)
        otp = random.randint(100000, 999999)
        cache.set(f"otp_{mobile}", otp, 300)

        try:
            send_sms_otp(mobile, otp)
        except Exception as e:
            return Response({
                "success": False,
                "error": "Failed to resend OTP",
                "details": str(e)
            }, status=500)

        return Response({
            "success": True,
            "message": "OTP resent successfully",
            "mobile": mobile
        })

class VerifyOTPView(APIView):
    permission_classes = []

    def post(self, request):
        mobile = request.data.get("mobile")
        otp_entered = request.data.get("otp")

        if not validate_mobile(mobile):
            return Response({"success": False, "error": "Invalid mobile number"}, status=400)

        if not otp_entered:
            return Response({"success": False, "error": "OTP is required"}, status=400)

        cached_otp = cache.get(f"otp_{mobile}")

        if not cached_otp:
            return Response({"success": False, "error": "OTP expired or not sent"}, status=400)

        if str(cached_otp) != str(otp_entered):
            return Response({"success": False, "error": "Invalid OTP"}, status=400)

        
        return Response({
            "success": True,
            "message": "OTP verified successfully",
            "mobile": mobile
        })