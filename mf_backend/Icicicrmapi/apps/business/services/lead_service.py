import json
import logging
from typing import Dict, Any

from django.db import transaction

from apps.business.services.base_service import BaseService
from apps.data.repositories.lead_repository import LeadRepository
from apps.data.repositories.log_repository import (
    RequestLogRepository,
    ResponseLogRepository
)
from apps.data.repositories.app_settings_repository import AppSettingsRepository
from apps.validators.lead_validator import LeadValidator
from apps.common.exceptions.base_exception import BusinessRuleException
from apps.common.constants.error_codes import ErrorCode
from apps.integrations.icici.lead_client import ICICILeadClient

logger = logging.getLogger(__name__)


class LeadService(BaseService):
    """
    Main business service for ICICI CRM Lead operations.
    """

    def __init__(
        self,
        lead_repo: LeadRepository,
        request_log_repo: RequestLogRepository,
        response_log_repo: ResponseLogRepository,
        settings_repo: AppSettingsRepository,
        validator: LeadValidator,
        icici_client: ICICILeadClient
    ):
        super().__init__()

        self._lead_repo = lead_repo
        self._request_log_repo = request_log_repo
        self._response_log_repo = response_log_repo
        self._settings_repo = settings_repo
        self._validator = validator
        self._icici_client = icici_client

    @transaction.atomic
    def push_lead_to_crm(
        self,
        lead_data: Dict[str, Any],
        correlation_id: str
    ) -> Dict[str, Any]:

        mobile_number = (
            lead_data.get("mobileNumber")
            or lead_data.get("mobile_number")
        )

        logger.info(
            f"PushLeadCustomerCrmDetails started for mobile: {mobile_number}"
        )

        # ------------------------------------------------------------------
        # Normalize request body (camelCase -> snake_case)
        # ------------------------------------------------------------------

        normalized_data = {
            "user_id": lead_data.get("userId") or lead_data.get("user_id"),
            "bank_id": lead_data.get("bankId") or lead_data.get("bank_id"),
            "first_name": lead_data.get("firstName") or lead_data.get("first_name"),
            "last_name": lead_data.get("lastName") or lead_data.get("last_name"),
            "mobile_number": mobile_number,
        }

        # ------------------------------------------------------------------
        # Validation
        # ------------------------------------------------------------------

        self._validator.validate_lead_push(normalized_data)

        # ------------------------------------------------------------------
        # Fetch App Settings
        # ------------------------------------------------------------------

        bank_id = normalized_data.get("bank_id") or 1

        settings = self._settings_repo.get_by_bank_id(bank_id)

        if not settings:
            raise BusinessRuleException(
                message="ICICI App Settings are not configured for this bank.",
                code=ErrorCode.SVC_NOT_FOUND
            )

        # ------------------------------------------------------------------
        # Save Lead
        # ------------------------------------------------------------------

        lead_instance = self._lead_repo.create(
            user_id=normalized_data["user_id"],
            bank_id=bank_id,
            first_name=normalized_data["first_name"],
            last_name=normalized_data["last_name"],
            mobile_number=normalized_data["mobile_number"],
            lead_source=settings.lead_source,
            country_code=settings.country_code,
            product=settings.product,
            lead_channel=settings.lead_channel,
            partner_id=settings.partner_id
        )

        # ------------------------------------------------------------------
        # ICICI Integration
        # ------------------------------------------------------------------

        try:

            plain_payload = self._build_full_integration_payload(
                lead_instance,
                settings
            )

            plain_payload_json = json.dumps(plain_payload)

            # --------------------------------------------------------------
            # Save Request Log
            # --------------------------------------------------------------

            request_log = self._request_log_repo.create(
                mobile_number=lead_instance.mobile_number,
                plain_request=plain_payload_json,
                encrypted_request="",
                correlation_id=correlation_id
            )

            # --------------------------------------------------------------
            # Call ICICI API
            # --------------------------------------------------------------

            api_result = self._icici_client.push_lead(
                plain_payload,
                settings
            )

            # --------------------------------------------------------------
            # Save Response Log
            # --------------------------------------------------------------

            self._response_log_repo.create(
                request_log=request_log,
                encrypted_response=api_result.get(
                    "encrypted_response",
                    ""
                ),
                plain_response=api_result.get(
                    "plain_response",
                    ""
                ),
                lead_number=api_result.get(
                    "lead_number",
                    ""
                ),
                lead_number_id=lead_instance.id,
                status_code=api_result.get(
                    "status_code",
                    ""
                ),
                correlation_id=correlation_id
            )

            # --------------------------------------------------------------
            # Update Request Log
            # --------------------------------------------------------------

            self._request_log_repo.update(
                request_log,
                encrypted_request=api_result.get(
                    "encrypted_request",
                    ""
                )
            )

            # --------------------------------------------------------------
            # Update Lead Number
            # --------------------------------------------------------------

            if api_result.get("lead_number"):

                self._lead_repo.update(
                    lead_instance,
                    icici_lead_number=api_result["lead_number"]
                )

            logger.info(
                f"Lead pushed successfully for mobile: {mobile_number}"
            )

            return {
                "success": api_result.get("success", True),
                "lead_number": api_result.get("lead_number"),
                "message": api_result.get(
                    "message",
                    "Lead pushed successfully"
                )
            }

        except Exception as ex:

            logger.exception(
                f"ICICI Integration Error for mobile "
                f"{mobile_number}: {str(ex)}"
            )

            raise

    def _build_full_integration_payload(
        self,
        lead,
        settings
    ) -> Dict[str, Any]:

        return {
            "IsAsync": settings.is_async,
            "CallBackUrl": settings.call_back_url,
            "LeadType": "",
            "LeadDetails": {
                "LeadNumber": "",
                "CountryCode": settings.country_code.strip(),
                "MobileNumber": lead.mobile_number,
                "Product": settings.product,
                "ProductSubType": "",
                "AlternateContactNumber": "",
                "LeadStatus": "",
                "LeadType": "",
                "AssignedToSelf": "",
                "AssignmentBasedOn": "",
                "BranchSolId": "",
                "CustomerType": "",
                "Salutation": "",
                "FirstName": lead.first_name,
                "MiddleName": "",
                "LastName": lead.last_name,
                "LeadSource": settings.lead_source,
                "PartnerId": settings.partner_id,
                "CampaignName": "",
                "AccountNumber": "",
                "AccountType": "",
                "Remarks": "",
                "LeadChannel": settings.lead_channel,
                "DateOfBirth": "",
                "Nationality": "",
                "PANNumber": "",
                "Gender": "",
                "ServiceFlag": "",
                "EmailAddress": "",
                "ResidencePhone": "",
                "OfficePhone": "",
                "ResidencyStatus": "",
                "PreferredCallTime": "",
                "PreferredCallStartTime": "",
                "PreferredCallEndTime": "",
                "ModeOfCommunication": "",
                "timezone": "",
                "overseascountry": "",
                "CustomerSegment": "",
                "AssignmentType": "",
                "AssignmentId": "",
                "ReferralType": "",
                "ReferredByOtherName": "",
                "ReferredByOtherEmail": "",
                "ReferredByOtherPhone": "",
                "ReferrerEmployeeId": "",
                "ReferredByLeadId": "",
                "ReferredByChannelPartnerId": "",
                "CustomerId": "",
                "UCIC": "",
                "ReferrerCustomerId": "",
                "ReferrerUCIC": "",
                "ReferrerPanNumber": "",
                "ReferrerUCC": "",
                "ReferrerAccountNumber": "",
                "ReferrerMobileNumber": "",
                "CVCESegment": "",
                "AffluentCustomer": False,
                "UTMCampaign": "",
                "UTMFEDID": "",
                "UTMGAID": "",
                "UTMGCIID": "",
                "UTMITM": "",
                "UTMLeadPriority": "",
                "UTMLeadPropensity": "",
                "UTMLeadScore": "",
                "UTMNTBID": "",
                "AggregatorLeadSource": "",
                "SMSShortCode": "",
                "PincodeLead": "",
                "DropOffPageName": "",
                "DropoffPageNumber": "",
                "TimeSpentonPage": "",
                "BREResponse": "",
                "FirstTimePAOfferFlag": "",
                "PAOffer": "",
                "TimeOfLeadDrop": "",
                "UTMLms": "",
                "Medium": "",
                "OnlineCoversionSR": "",
                "UotmCode": "",
                "UTMInfo": "",
                "Priority": "",
                "IndividualOrganizationName": "",
                "ReferrerOrganizationName": "",
                "LeadGenerator": ""
            },
            "AddressDetails": [
                {
                    "AddressType": "",
                    "AddressLine1": "",
                    "AddressLine2": "",
                    "AddressLine3": "",
                    "AddressLine4": "",
                    "Landmark": "",
                    "Locality": "",
                    "Village": "",
                    "City": "",
                    "District": "",
                    "State": "",
                    "Country": "",
                    "Pincode": "",
                    "Latitude": "",
                    "Longitude": ""
                }
            ],
            "OrganisationDetails": {
                "CompanyName": "",
                "AccountNumber": "",
                "UCC": "",
                "PpaCode": "",
                "MobileNo": "",
                "EmailAddress": "",
                "PanNumber": "",
                "DateOfIncorporation": "",
                "ContactPersonFirstName": "",
                "ContactPersonMiddleName": "",
                "ContactPersonLastName": "",
                "ContactPersonMobileNumber": "",
                "ContactPersonPanNumber": "",
                "ContactPersonUCIC": ""
            },
            "AppointmentDetails": {
                "EngagementType": "",
                "IsJointActivity": "",
                "InitiatedBy": "",
                "PurposeOfMeeting": "",
                "PlaceOfMeeting": "",
                "StartDateTime": "",
                "AppointmentStatus": ""
            },
            "ApplicationDetails": {
                "GoldLoanRequest": {
                    "TransactionId": "",
                    "LoanAmount": "",
                    "LoanTenure": "",
                    "LoanAccountNumber": "",
                    "LoanAmountDisbursed": "",
                    "DisbursalDate": "",
                    "InstanceId": "",
                    "ROI": "",
                    "ApplicantId_CustId": "",
                    "AssessmentId": "",
                    "VariantFacilityType": "",
                    "Gender": "",
                    "MaritalStatus": "",
                    "Religion": "",
                    "Education": "",
                    "SourceOfFunds": "",
                    "GrossAnnualIncome": "",
                    "PersonWithDisability": "",
                    "VernacularDeclaration": "",
                    "FatherName": "",
                    "MotherMaidenName": "",
                    "SubAgentCode": getattr(settings, 'sub_agent_code', "")
                }
            }
        }