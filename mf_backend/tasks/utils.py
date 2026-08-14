# utils/otp_utils.py
import random, datetime
import pytz
from django.utils import timezone
from utils.envSetup import environment

def generate_otp():
    return str(random.randint(100000, 999999))

# def is_otp_valid(tracker, otp):
#     """Check if OTP matches and is within 5 minutes validity."""
#     if not tracker.pan_otp or not tracker.pan_otp_created_at:
#         return False
#     time_diff = timezone.now() - tracker.pan_otp_created_at
#     if tracker.pan_otp == otp and time_diff.total_seconds() <= 300:  # 5 min
#         return True
#     return False

def is_otp_valid(obj, otp):
    """
    Validates OTP for both:
    - SubTaskTracker (pan_otp)
    - User (phone_otp)
    """

    try:
        if getattr(environment, "MASTER_OTP", None) and str(otp) == str(environment.MASTER_OTP):
            return True
    except Exception:
        pass

    # Tracker OTP fields
    obj_otp = getattr(obj, "pan_otp", None)
    obj_otp_created = getattr(obj, "pan_otp_created_at", None)

    # If OTP not found on tracker → check User fields
    if obj_otp is None and hasattr(obj, "phone_otp"):
        obj_otp = getattr(obj, "phone_otp", None)
        obj_otp_created = getattr(obj, "phone_otp_created_at", None)

    # OTP or timestamp missing
    if not obj_otp or not obj_otp_created:
        return False

    # Expiry check 5 minutes
    time_diff = timezone.now() - obj_otp_created

    if obj_otp == otp and time_diff.total_seconds() <= 300:
        return True

    return False


def get_ist_time_str():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = timezone.now().astimezone(ist)
    return now_ist.strftime("%d-%m-%Y %I:%M %p")  # e.g., "25-02-2026 02:45 PM"


def to_bool(val):
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ["true", "1", "yes"]
