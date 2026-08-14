from django.db import models
from apps.models.base_model import BaseModel


class LeadAddressDetail(BaseModel):
    """
    Model to store address details associated with a lead.
    """
    lead = models.ForeignKey("apps.CustomerCrmLead", on_delete=models.CASCADE, related_name="address_details")
    address_type = models.CharField(max_length=50, blank=True, default="")
    address_line_1 = models.CharField(max_length=255, blank=True, default="")
    address_line_2 = models.CharField(max_length=255, blank=True, default="")
    address_line_3 = models.CharField(max_length=255, blank=True, default="")
    address_line_4 = models.CharField(max_length=255, blank=True, default="")
    landmark = models.CharField(max_length=100, blank=True, default="")
    locality = models.CharField(max_length=100, blank=True, default="")
    village = models.CharField(max_length=100, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    district = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="India")
    pincode = models.CharField(max_length=10, blank=True, default="")
    latitude = models.CharField(max_length=50, blank=True, default="")
    longitude = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        db_table = "lead_address_details"
        verbose_name = "Lead Address Detail"
        verbose_name_plural = "Lead Address Details"


class LeadOrganisationDetail(BaseModel):
    """
    Model to store organisation details associated with a lead.
    """
    lead = models.OneToOneField("apps.CustomerCrmLead", on_delete=models.CASCADE, related_name="organisation_details")
    company_name = models.CharField(max_length=200, blank=True, default="")
    account_number = models.CharField(max_length=50, blank=True, default="")
    ucc = models.CharField(max_length=100, blank=True, default="")
    ppa_code = models.CharField(max_length=50, blank=True, default="")
    mobile_no = models.CharField(max_length=20, blank=True, default="")
    email_address = models.EmailField(max_length=255, blank=True, default="")
    pan_number = models.CharField(max_length=20, blank=True, default="")
    date_of_incorporation = models.CharField(max_length=50, blank=True, default="")
    
    # Contact Person Details
    contact_person_first_name = models.CharField(max_length=100, blank=True, default="")
    contact_person_middle_name = models.CharField(max_length=100, blank=True, default="")
    contact_person_last_name = models.CharField(max_length=100, blank=True, default="")
    contact_person_mobile_number = models.CharField(max_length=20, blank=True, default="")
    contact_person_pan_number = models.CharField(max_length=20, blank=True, default="")
    contact_person_ucic = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        db_table = "lead_organisation_details"
        verbose_name = "Lead Organisation Detail"


class LeadAppointmentDetail(BaseModel):
    """
    Model to store appointment details for a lead.
    """
    lead = models.OneToOneField("apps.CustomerCrmLead", on_delete=models.CASCADE, related_name="appointment_details")
    engagement_type = models.CharField(max_length=50, blank=True, default="")
    is_joint_activity = models.CharField(max_length=10, blank=True, default="")
    initiated_by = models.CharField(max_length=100, blank=True, default="")
    purpose_of_meeting = models.CharField(max_length=200, blank=True, default="")
    place_of_meeting = models.CharField(max_length=200, blank=True, default="")
    start_date_time = models.CharField(max_length=50, blank=True, default="")
    appointment_status = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        db_table = "lead_appointment_details"
        verbose_name = "Lead Appointment Detail"


class GoldLoanRequest(BaseModel):
    """
    Model to store Gold Loan specific request details.
    """
    lead = models.ForeignKey("apps.CustomerCrmLead", on_delete=models.CASCADE, related_name="gold_loan_requests")
    transaction_id = models.CharField(max_length=100, blank=True, default="")
    loan_amount = models.CharField(max_length=50, blank=True, default="")
    loan_tenure = models.CharField(max_length=20, blank=True, default="")
    loan_account_number = models.CharField(max_length=50, blank=True, default="")
    loan_amount_disbursed = models.CharField(max_length=50, blank=True, default="")
    disbursal_date = models.CharField(max_length=50, blank=True, default="")
    instance_id = models.CharField(max_length=100, blank=True, default="")
    roi = models.CharField(max_length=20, blank=True, default="")
    applicant_id_cust_id = models.CharField(max_length=100, blank=True, default="")
    assessment_id = models.CharField(max_length=100, blank=True, default="")
    variant_facility_type = models.CharField(max_length=100, blank=True, default="")
    gender = models.CharField(max_length=20, blank=True, default="")
    marital_status = models.CharField(max_length=50, blank=True, default="")
    religion = models.CharField(max_length=50, blank=True, default="")
    education = models.CharField(max_length=100, blank=True, default="")
    source_of_funds = models.CharField(max_length=100, blank=True, default="")
    gross_annual_income = models.CharField(max_length=50, blank=True, default="")
    person_with_disability = models.CharField(max_length=10, blank=True, default="")
    vernacular_declaration = models.CharField(max_length=10, blank=True, default="")
    father_name = models.CharField(max_length=100, blank=True, default="")
    mother_maiden_name = models.CharField(max_length=100, blank=True, default="")
    sub_agent_code = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        db_table = "gold_loan_requests"
        verbose_name = "Gold Loan Request"
        verbose_name_plural = "Gold Loan Requests"
