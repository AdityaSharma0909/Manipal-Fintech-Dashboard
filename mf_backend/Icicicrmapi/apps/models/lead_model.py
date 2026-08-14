from django.db import models
from apps.models.base_model import BaseModel


class CustomerCrmLead(BaseModel):
    """
    Model to store extensive customer lead details pushed to ICICI CRM.
    """
    # Identification
    user_id = models.CharField(max_length=100, help_text="Identifier for the user who initiated the lead")
    bank_id = models.IntegerField(help_text="Identifier for the bank", db_index=True)
    icici_lead_number = models.CharField(max_length=100, blank=True, null=True, db_index=True, help_text="Lead ID returned by ICICI")
    
    # Core Customer Details
    salutation = models.CharField(max_length=20, blank=True, default="")
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, default="")
    last_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20, db_index=True)
    alternate_contact_number = models.CharField(max_length=20, blank=True, default="")
    email_address = models.EmailField(max_length=255, blank=True, default="")
    date_of_birth = models.CharField(max_length=50, blank=True, default="")
    gender = models.CharField(max_length=20, blank=True, default="")
    nationality = models.CharField(max_length=50, blank=True, default="")
    pan_number = models.CharField(max_length=20, blank=True, default="", db_index=True)
    
    # Lead Meta
    lead_source = models.CharField(max_length=100, blank=True, default="")
    lead_status = models.CharField(max_length=50, blank=True, default="")
    lead_type = models.CharField(max_length=50, blank=True, default="")
    lead_channel = models.CharField(max_length=100, blank=True, default="")
    product = models.CharField(max_length=100, blank=True, default="")
    product_sub_type = models.CharField(max_length=100, blank=True, default="")
    country_code = models.CharField(max_length=10, blank=True, default="")
    
    # Assignment & Sourcing
    assigned_to_self = models.CharField(max_length=10, blank=True, default="")
    assignment_based_on = models.CharField(max_length=50, blank=True, default="")
    assignment_type = models.CharField(max_length=50, blank=True, default="")
    assignment_id = models.CharField(max_length=100, blank=True, default="")
    branch_sol_id = models.CharField(max_length=50, blank=True, default="")
    partner_id = models.CharField(max_length=100, blank=True, default="")
    campaign_name = models.CharField(max_length=100, blank=True, default="")
    lead_generator = models.CharField(max_length=100, blank=True, default="")
    
    # Account Info
    customer_type = models.CharField(max_length=50, blank=True, default="")
    customer_id = models.CharField(max_length=100, blank=True, default="")
    ucic = models.CharField(max_length=100, blank=True, default="")
    account_number = models.CharField(max_length=50, blank=True, default="")
    account_type = models.CharField(max_length=50, blank=True, default="")
    
    # Contact Details
    residence_phone = models.CharField(max_length=20, blank=True, default="")
    office_phone = models.CharField(max_length=20, blank=True, default="")
    residency_status = models.CharField(max_length=50, blank=True, default="")
    preferred_call_time = models.CharField(max_length=50, blank=True, default="")
    preferred_call_start_time = models.CharField(max_length=50, blank=True, default="")
    preferred_call_end_time = models.CharField(max_length=50, blank=True, default="")
    mode_of_communication = models.CharField(max_length=50, blank=True, default="")
    timezone = models.CharField(max_length=50, blank=True, default="")
    overseas_country = models.CharField(max_length=50, blank=True, default="")
    customer_segment = models.CharField(max_length=100, blank=True, default="")
    
    # Referral Info
    referral_type = models.CharField(max_length=50, blank=True, default="")
    referred_by_other_name = models.CharField(max_length=100, blank=True, default="")
    referred_by_other_email = models.CharField(max_length=100, blank=True, default="")
    referred_by_other_phone = models.CharField(max_length=20, blank=True, default="")
    referrer_employee_id = models.CharField(max_length=50, blank=True, default="")
    referred_by_lead_id = models.CharField(max_length=100, blank=True, default="")
    referred_by_channel_partner_id = models.CharField(max_length=100, blank=True, default="")
    referrer_customer_id = models.CharField(max_length=100, blank=True, default="")
    referrer_ucic = models.CharField(max_length=100, blank=True, default="")
    referrer_pan_number = models.CharField(max_length=20, blank=True, default="")
    referrer_ucc = models.CharField(max_length=100, blank=True, default="")
    referrer_account_number = models.CharField(max_length=50, blank=True, default="")
    referrer_mobile_number = models.CharField(max_length=20, blank=True, default="")
    referrer_organization_name = models.CharField(max_length=200, blank=True, default="")
    
    # Marketing & Tracking (UTM)
    cvce_segment = models.CharField(max_length=100, blank=True, default="")
    affluent_customer = models.BooleanField(default=False)
    utm_campaign = models.CharField(max_length=200, blank=True, default="")
    utm_fed_id = models.CharField(max_length=100, blank=True, default="")
    utm_ga_id = models.CharField(max_length=100, blank=True, default="")
    utm_gci_id = models.CharField(max_length=100, blank=True, default="")
    utm_itm = models.CharField(max_length=100, blank=True, default="")
    utm_lead_priority = models.CharField(max_length=50, blank=True, default="")
    utm_lead_propensity = models.CharField(max_length=50, blank=True, default="")
    utm_lead_score = models.CharField(max_length=50, blank=True, default="")
    utm_ntb_id = models.CharField(max_length=100, blank=True, default="")
    utm_lms = models.CharField(max_length=100, blank=True, default="")
    utm_info = models.TextField(blank=True, default="")
    aggregator_lead_source = models.CharField(max_length=100, blank=True, default="")
    sms_short_code = models.CharField(max_length=50, blank=True, default="")
    medium = models.CharField(max_length=50, blank=True, default="")
    uotm_code = models.CharField(max_length=100, blank=True, default="")
    
    # Operational Tracking
    pincode_lead = models.CharField(max_length=10, blank=True, default="")
    drop_off_page_name = models.CharField(max_length=100, blank=True, default="")
    dropoff_page_number = models.CharField(max_length=50, blank=True, default="")
    time_spent_on_page = models.CharField(max_length=50, blank=True, default="")
    bre_response = models.TextField(blank=True, default="")
    first_time_pa_offer_flag = models.CharField(max_length=10, blank=True, default="")
    pa_offer = models.CharField(max_length=100, blank=True, default="")
    time_of_lead_drop = models.CharField(max_length=50, blank=True, default="")
    online_coversion_sr = models.CharField(max_length=100, blank=True, default="")
    priority = models.CharField(max_length=50, blank=True, default="")
    individual_organization_name = models.CharField(max_length=200, blank=True, default="")
    remarks = models.TextField(blank=True, default="")
    service_flag = models.CharField(max_length=10, blank=True, default="")

    class Meta:
        db_table = "customer_crm_leads"
        verbose_name = "Customer CRM Lead"
        verbose_name_plural = "Customer CRM Leads"
        indexes = [
            models.Index(fields=["mobile_number"], name="idx_lead_mobile"),
            models.Index(fields=["bank_id"], name="idx_lead_bank"),
            models.Index(fields=["pan_number"], name="idx_lead_pan"),
            models.Index(fields=["icici_lead_number"], name="idx_lead_icici_no"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mobile_number}) - {self.icici_lead_number or 'PENDING'}"
