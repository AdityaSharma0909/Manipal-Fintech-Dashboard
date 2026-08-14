from django.db import models

# PanVerification Model
class PanVerification(models.Model):
    # Response meta info
    request_id = models.CharField(max_length=100, blank=True, null=True)
    task_id = models.CharField(max_length=100, blank=True, null=True)
    group_id = models.CharField(max_length=100, blank=True, null=True)
    response_code = models.CharField(max_length=20, blank=True, null=True)
    response_message = models.CharField(max_length=255, blank=True, null=True)
    billable = models.CharField(max_length=5, blank=True, null=True)

    # PAN result details
    pan_number = models.CharField(max_length=20)
    pan_holder_name = models.CharField(max_length=150)
    name_match_score = models.CharField(max_length=10, blank=True, null=True)
    pan_type = models.CharField(max_length=50, blank=True, null=True)
    aadhaar_linked_status = models.BooleanField(default=False)
    masked_aadhaar = models.CharField(max_length=20, blank=True, null=True)
    user_email = models.EmailField(blank=True, null=True)
    user_phone_number = models.CharField(max_length=20, blank=True, null=True)
    user_gender = models.CharField(max_length=10, blank=True, null=True)
    user_dob = models.CharField(max_length=20, blank=True, null=True)

    # Address
    user_address = models.JSONField(blank=True, null=True)

    # Timestamps
    request_timestamp = models.CharField(max_length=50, blank=True, null=True)
    response_timestamp = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pan_number} - {self.pan_holder_name}"

# BankVerification Model
class BankVerification(models.Model):
    # Request Data
    account_number = models.CharField(max_length=50)
    ifsc = models.CharField(max_length=20)
    name_to_match = models.CharField(max_length=100)
    consent = models.CharField(max_length=1, default='Y')
    consent_text = models.TextField(default="I hereby declare my consent agreement for fetching my information via ZOOP API")
    task_id = models.CharField(max_length=100, blank=True, null=True)

    # Response Data
    request_id = models.CharField(max_length=100, blank=True, null=True)
    group_id = models.CharField(max_length=100, blank=True, null=True)
    success = models.BooleanField(default=False)
    response_code = models.CharField(max_length=50, blank=True, null=True)
    response_message = models.CharField(max_length=200, blank=True, null=True)
    beneficiary_name = models.CharField(max_length=150, blank=True, null=True)
    verification_status = models.CharField(max_length=50, blank=True, null=True)
    name_match_score = models.CharField(max_length=50, blank=True, null=True)
    transaction_remark = models.CharField(max_length=200, blank=True, null=True)

    # IFSC details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Penny Drop Fields
    is_penny_drop = models.BooleanField(default=False)
    penny_drop_amount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    penny_drop_txn_ref = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account_number} - {self.verification_status}"


# DrivingLicenceVerification Model
class DrivingLicenceVerification(models.Model):
    customer_dl_number = models.CharField(max_length=20)
    name_to_match = models.CharField(max_length=100)
    customer_dob = models.CharField(max_length=20)
    consent = models.CharField(max_length=5, default='Y')
    consent_text = models.TextField()

    # Response fields
    request_id = models.CharField(max_length=100, null=True, blank=True)
    task_id = models.CharField(max_length=100, null=True, blank=True)
    group_id = models.CharField(max_length=100, null=True, blank=True)
    success = models.BooleanField(default=False)
    response_code = models.CharField(max_length=10, null=True, blank=True)
    response_message = models.CharField(max_length=255, null=True, blank=True)

    # DL Info
    user_full_name = models.CharField(max_length=100, null=True, blank=True)
    user_dob = models.CharField(max_length=20, null=True, blank=True)
    father_or_husband = models.CharField(max_length=100, null=True, blank=True)
    dl_number = models.CharField(max_length=50, null=True, blank=True)
    expiry_date = models.CharField(max_length=20, null=True, blank=True)
    user_blood_group = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    name_match_score = models.CharField(max_length=10, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    # Address fields
    address = models.TextField(null=True, blank=True)
    pin = models.CharField(max_length=10, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    address_type = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_dl_number} - {self.user_full_name or 'Unknown'}"



class ChequeOCRVerification(models.Model):
    cheque_image = models.TextField()  # store base64 or file path
    consent = models.CharField(max_length=5, default='Y')
    consent_text = models.TextField()

    # Response fields
    request_id = models.CharField(max_length=100, null=True, blank=True)
    task_id = models.CharField(max_length=100, null=True, blank=True)
    group_id = models.CharField(max_length=100, null=True, blank=True)
    success = models.BooleanField(default=False)
    response_code = models.CharField(max_length=10, null=True, blank=True)
    response_message = models.CharField(max_length=255, null=True, blank=True)

    # Cheque details
    bank = models.CharField(max_length=100, null=True, blank=True)
    ifsc_code = models.CharField(max_length=50, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    branch = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)

    request_timestamp = models.CharField(max_length=50, null=True, blank=True)
    response_timestamp = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChequeOCR - {self.bank or 'Unknown Bank'}"




class OCRLiteVerification(models.Model):
    CARD_TYPE_CHOICES = [
        ("PAN", "PAN Card"),
        ("AADHAAR", "Aadhaar Card"),
        ("DRIVING_LICENSE", "Driving License"),
        ("VOTER_ID", "Voter ID"),
        ("PASSPORT", "Passport"),
        ("OTHER", "Other"),
    ]
    card_front_image = models.ImageField(upload_to='ocr_lite/', null=True, blank=True)
    card_back_image = models.ImageField(upload_to='ocr_lite/', null=True, blank=True)

    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default="PAN")
    consent = models.CharField(max_length=1, default="Y")
    consent_text = models.TextField(default="I hereby declare my consent agreement for fetching my information via Zoop API")
    task_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OCR Lite - {self.card_type}"


class VoterIDAdvanceVerification(models.Model):
    # Input fields
    customer_epic_number = models.CharField(max_length=50)
    name_to_match = models.CharField(max_length=100)
    consent = models.CharField(max_length=1, default="Y")
    consent_text = models.TextField(default="I hereby consent")
    task_id = models.CharField(max_length=100, blank=True, null=True)

    # Zoop response fields
    request_id = models.CharField(max_length=100, null=True, blank=True)
    group_id = models.CharField(max_length=100, null=True, blank=True)
    success = models.BooleanField(default=False)
    response_code = models.CharField(max_length=10, null=True, blank=True)
    response_message = models.CharField(max_length=255, null=True, blank=True)

    # Result fields
    user_name_english = models.CharField(max_length=200, null=True, blank=True)
    user_name_vernacular = models.CharField(max_length=200, null=True, blank=True)
    user_gender = models.CharField(max_length=10, null=True, blank=True)
    user_age = models.IntegerField(null=True, blank=True)

    relative_name_english = models.CharField(max_length=200, null=True, blank=True)
    relative_name_vernacular = models.CharField(max_length=200, null=True, blank=True)
    relative_relation = models.CharField(max_length=20, null=True, blank=True)

    assembly_constituency_name = models.CharField(max_length=200, null=True, blank=True)
    constituency_part_number = models.IntegerField(null=True, blank=True)
    serial_number_applicable_part = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, null=True, blank=True)

    voter_last_updated_date = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_epic_number


class PassportAdvanceVerification(models.Model):
    # Input fields
    customer_file_number = models.CharField(max_length=50)
    name_to_match = models.CharField(max_length=100)
    customer_dob = models.CharField(max_length=20)  # "DD-MM-YYYY"
    consent = models.CharField(max_length=1, default="Y")
    consent_text = models.TextField(default="I hereby give my consent")
    task_id = models.CharField(max_length=100, blank=True, null=True)

    # Zoop API fields
    request_id = models.CharField(max_length=100, null=True, blank=True)
    group_id = models.CharField(max_length=100, null=True, blank=True)
    success = models.BooleanField(default=False)
    response_code = models.CharField(max_length=10, null=True, blank=True)
    response_message = models.CharField(max_length=255, null=True, blank=True)

    # Result fields
    passport_status = models.BooleanField(null=True, blank=True)
    name_on_passport = models.CharField(max_length=200, null=True, blank=True)
    customer_last_name = models.CharField(max_length=200, null=True, blank=True)
    passport_number = models.CharField(max_length=50, null=True, blank=True)
    passport_applied_date = models.CharField(max_length=50, null=True, blank=True)
    name_match_score = models.CharField(max_length=10, null=True, blank=True)

    customer_dob_result = models.CharField(max_length=20, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_file_number


class FaceMatchVerification(models.Model):
    # Input fields (Base64 strings as per curl)
    card_image = models.TextField()  # Base64 string
    user_image = models.TextField()  # Base64 string
    consent = models.CharField(max_length=1, default="Y")
    consent_text = models.TextField(default="I hereby declare my consent agreement for fetching my information via ZOOP API")
    task_id = models.CharField(max_length=100, blank=True, null=True)

    # Response fields
    request_id = models.CharField(max_length=100, null=True, blank=True)
    group_id = models.CharField(max_length=100, null=True, blank=True)
    success = models.BooleanField(default=False)
    response_code = models.CharField(max_length=10, null=True, blank=True)
    response_message = models.CharField(max_length=255, null=True, blank=True)

    # Metadata fields
    billable = models.CharField(max_length=5, null=True, blank=True)
    reason_message = models.CharField(max_length=255, null=True, blank=True)

    # Result field
    face_match_score = models.CharField(max_length=10, null=True, blank=True)

    # Timestamps
    request_timestamp = models.CharField(max_length=50, null=True, blank=True)
    response_timestamp = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FaceMatch - {self.face_match_score or 'N/A'}"
