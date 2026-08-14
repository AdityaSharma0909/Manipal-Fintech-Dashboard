from typing import Any, Dict, Tuple
from onboarding_v2.models import LeadV2, PincodeMaster
from .settings import ICICIConfig

def _split_name(full_name: str) -> Tuple[str, str, str]:
    parts = [p for p in (full_name or "").strip().split() if p]
    if not parts:
        return ("", "", "")
    if len(parts) == 1:
        return (parts[0], "", "")
    if len(parts) == 2:
        return (parts[0], "", parts[1])
    return (parts[0], " ".join(parts[1:-1]), parts[-1])

def build_icici_lead_payload(lead: LeadV2, config: ICICIConfig) -> Dict[str, Any]:
    first, middle, last = _split_name(lead.customer_name)
    
    meta = lead.metadata or {}
    
    # Map gender to ICICI format (usually M/F)
    gender = (lead.gender or "").upper()
    icici_gender = ""
    if gender in ("MALE", "M"):
        icici_gender = "M"
    elif gender in ("FEMALE", "F"):
        icici_gender = "F"
    
    # Map salutation based on gender if not provided
    salutation = meta.get("salutation")
    if not salutation:
        if icici_gender == "F":
            salutation = "Ms"
        else:
            salutation = "Mr"

    # Try to resolve city/state from pincode
    city = meta.get("city")
    state = meta.get("state")
    district = meta.get("district")
    if lead.pincode and (not city or not state):
        try:
            pincode_record = PincodeMaster.objects.filter(pincode=lead.pincode).first()
            if pincode_record:
                city = city or pincode_record.regionname or pincode_record.district
                state = state or pincode_record.statename
                district = district or pincode_record.district
        except Exception:
            pass
    
    city = city or "City"
    state = state or "State"

    # return {
    #     "IsAsync": False,
    #     "CallBackUrl": "",
    #     "LeadType": "FRESH",
    #     "LeadDetails": {
    #         "LeadNumber": "",
    #         "CountryCode": "+91",
    #         "MobileNumber": lead.contact_number[-10:] if lead.contact_number else "", # Ensure 10 digits
    #         "Product": "CRM728",
    #         "ProductSubType": lead.product_subcategory or "",
    #         "AlternateContactNumber": meta.get("alternate_mobile", ""),
    #         "LeadStatus": "ACTIVE",
    #         "LeadType": "FRESH",
    #         "AssignedToSelf": "Y",
    #         "AssignmentBasedOn": "BRANCH",
    #         "BranchSolId": str(lead.bank_branch or meta.get("branch_sol_id") or ""),
    #         "CustomerType": "INDIVIDUAL",
    #         "Salutation": salutation,
    #         "FirstName": first,
    #         "MiddleName": middle,
    #         "LastName": last or ".", # Some APIs require a dot if last name is missing
    #         "LeadSource": "LSM0018",
    #         "PartnerId": config.partner_id,
    #         "CampaignName": meta.get("campaign_name", ""),
    #         "AccountNumber": "",
    #         "AccountType": "",
    #         "Remarks": "Lead created from Manipal Onboarding",
    #         "LeadChannel": config.lead_channel,
    #         "DateOfBirth": lead.dob.strftime("%d-%m-%Y") if lead.dob else "",
    #         "Nationality": "Indian",
    #         "PANNumber": lead.pan_number or "",
    #         "Gender": icici_gender,
    #         "ServiceFlag": "",
    #         "EmailAddress": lead.email_address or "",
    #         "ResidencePhone": "",
    #         "OfficePhone": "",
    #         "ResidencyStatus": "Resident",
    #         "PincodeLead": lead.pincode or "",
    #     },
    #     "AddressDetails": [
    #         {
    #             "AddressType": "RESIDENCE",
    #             "AddressLine1": lead.address or "Address", # Ensure not empty
    #             "AddressLine2": "",
    #             "AddressLine3": "",
    #             "AddressLine4": "",
    #             "City": city,
    #             "District": district or "",
    #             "State": state,
    #             "Country": "IN", # Use IN for consistency
    #             "Pincode": lead.pincode or ""
    #         }
    #     ],
    #     "ApplicationDetails": {
    #         "GoldLoanRequest": {
    #             "TransactionId": str(lead.id),
    #             "LoanAmount": str(int(lead.amount)) if lead.amount is not None else "0", # Try integer string
    #             "SubAgentCode": config.sub_agent_code or "0" # Default to 0 if empty
    #         }
    #     }
    # }
    return {
   "IsAsync":"false",
   "CallBackUrl":"",
   "LeadType":"",
   "LeadDetails":{
      "LeadNumber":"",
      "CountryCode":"+91",
      "MobileNumber":lead.contact_number[-10:] if lead.contact_number else "",
      "Product":"CRM728",
      "ProductSubType":"",
      "AlternateContactNumber":"",
      "LeadStatus":"",
      "LeadType":"",
      "AssignedToSelf":"",
      "AssignmentBasedOn":"",
      "BranchSolId":"",
      "CustomerType":"",
      "Salutation":"",
      "FirstName":first or "",
      "MiddleName":middle or "",
      "LastName":last or "",
      "LeadSource":"LSM0018",
      "PartnerId":"PI07515",
      "CampaignName":"",
      "AccountNumber":"",
      "AccountType":"",
      "Remarks":"",
      "LeadChannel":"Digital",
      "DateOfBirth":"",
      "Nationality":"",
      "PANNumber":"",
      "Gender":"",
      "ServiceFlag":"",
      "EmailAddress":"",
      "ResidencePhone":"",
      "OfficePhone":"",
      "ResidencyStatus":"",
      "PreferredCallTime":"",
      "PreferredCallStartTime":"",
      "PreferredCallEndTime":"",
      "ModeOfCommunication":"",
      "timezone":"",
      "overseascountry":"",
      "CustomerSegment":"",
      "AssignmentType":"",
      "AssignmentId":"",
      "ReferralType":"",
      "ReferredByOtherName":"",
      "ReferredByOtherEmail":"",
      "ReferredByOtherPhone":"",
      "ReferrerEmployeeId":"",
      "ReferredByLeadId":"",
      "ReferredByChannelPartnerId":"",
      "CustomerId":"",
      "UCIC":"",
      "ReferrerCustomerId":"",
      "ReferrerUCIC":"",
      "ReferrerPanNumber":"",
      "ReferrerUCC":"",
      "ReferrerAccountNumber":"",
      "ReferrerMobileNumber":"",
      "CVCESegment":"",
      "AffluentCustomer":"false",
      "UTMCampaign":"",
      "UTMFEDID":"",
      "UTMGAID":"",
      "UTMGCIID":"",
      "UTMITM":"",
      "UTMLeadPriority":"",
      "UTMLeadPropensity":"",
      "UTMLeadScore":"",
      "UTMNTBID":"",
      "AggregatorLeadSource":"",
      "SMSShortCode":"",
      "PincodeLead":"",
      "DropOffPageName":"",
      "DropoffPageNumber":"",
      "TimeSpentonPage":"",
      "BREResponse":"",
      "FirstTimePAOfferFlag":"",
      "PAOffer":"",
      "TimeOfLeadDrop":"",
      "UTMLms":"",
      "Medium":"",
      "OnlineCoversionSR":"",
      "UotmCode":"",
      "UTMInfo":"",
      "Priority":"",
      "IndividualOrganizationName":"",
      "ReferrerOrganizationName":"",
      "LeadGenerator":""
   },
   "AddressDetails":[
      {
         "AddressType":"",
         "AddressLine1":"",
         "AddressLine2":"",
         "AddressLine3":"",
         "AddressLine4":"",
         "Landmark":"",
         "Locality":"",
         "Village":"",
         "City":"",
         "District":"",
         "State":"",
         "Country":"",
         "Pincode":"",
         "Latitude":"",
         "Longitude":""
      }
   ],
   "OrganisationDetails":{
      "CompanyName":"",
      "AccountNumber":"",
      "UCC":"",
      "PpaCode":"",
      "MobileNo":"",
      "EmailAddress":"",
      "PanNumber":"",
      "DateOfIncorporation":"",
      "ContactPersonFirstName":"",
      "ContactPersonMiddleName":"",
      "ContactPersonLastName":"",
      "ContactPersonMobileNumber":"",
      "ContactPersonPanNumber":"",
      "ContactPersonUCIC":""
   },
   "AppointmentDetails":{
      "EngagementType":"",
      "IsJointActivity":"",
      "InitiatedBy":"",
      "PurposeOfMeeting":"",
      "PlaceOfMeeting":"",
      "StartDateTime":"",
      "AppointmentStatus":""
   },
   "ApplicationDetails":{
      "GoldLoanRequest":{
         "TransactionId":"",
         "LoanAmount":"",
         "LoanTenure":"",
         "LoanAccountNumber":"",
         "LoanAmountDisbursed":"",
         "DisbursalDate":"",
         "InstanceId":"",
         "ROI":"",
         "ApplicantId_CustId":"",
         "AssessmentId":"",
         "VariantFacilityType":"",
         "Gender":"",
         "MaritalStatus":"",
         "Religion":"",
         "Education":"",
         "SourceOfFunds":"",
         "GrossAnnualIncome":"",
         "PersonWithDisability":"",
         "VernacularDeclaration":"",
         "FatherName":"",
         "MotherMaidenName":""
      }
   }
}
