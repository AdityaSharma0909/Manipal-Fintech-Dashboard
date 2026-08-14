import os
import uuid
import logging
import json
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from rest_framework import status

from crm_integration.exceptions import BajajFinServoApiException, TokenApiException
from crm_integration.utils.encryption import AESCryptoUtility, BYPASS_ENCRYPTION
from crm_integration.api_clients.token_providers import MicrosoftTokenProvider
from crm_integration.api_clients.bajaj_client import BajajFinServoApiClient
from crm_integration.repositories import LeadRepository
from crm_integration.models import LeadStatusChoices
from crm_integration.services.branch_lookup_service import BranchLookupService
from crm_integration.services.lead_type_configuration import LeadTypeConfigurationProvider

logger = logging.getLogger(__name__)


class TokenService:
    """Orchestrates token generation using Microsoft OAuth provider."""

    def __init__(self):
        self.token_provider = MicrosoftTokenProvider()

    async def get_access_token(self) -> str:
        return await self.token_provider.get_token()


class SaveFileService:
    """

    Serializes request-response payloads to disk text files.
    """

    def __init__(self):
        self.base_path = settings.FILE_STORAGE.get('BASE_PATH')
        if not self.base_path:
            raise ValueError("FileStorage:BASE_PATH is not configured.")

    async def save_lead_payload_to_file(self, lead_audit: dict) -> str:
        try:
            now = datetime.now()
            folder_path = os.path.join(
                self.base_path,
                str(now.year),
                f"{now.month:02d}",
                f"{now.day:02d}"
            )
            os.makedirs(folder_path, exist_ok=True)

            lead_id = lead_audit.get('LeadId', 0)
            time_str = datetime.utcnow().strftime("%H%M%S")
            unique_id = uuid.uuid4()

            file_name = f"BajajLead_{lead_id}_{time_str}_{unique_id}.txt"
            file_path = os.path.join(folder_path, file_name)

            file_content = f"""==============================
Bajaj FinServo Lead Log
LeadId        : {lead_id}
Date (UTC)    : {datetime.utcnow().isoformat()}
==============================

---- ENCRYPTED REQUEST ----
{lead_audit.get('EncryptedRequest', '')}

---- PLAIN REQUEST ----
{lead_audit.get('PlainRequest', '')}

---- ENCRYPTED RESPONSE ----
{lead_audit.get('EncryptedResponse', '')}

---- PLAIN RESPONSE ----
{lead_audit.get('PlainResponse', '')}"""

            import anyio
            await anyio.to_thread.run_sync(self._write_file, file_path, file_content)

            return file_path
        except Exception as ex:
            logger.exception(f"Failed to save lead payload for LeadId {lead_audit.get('LeadId')}")
            return ""

    def _write_file(self, path, content):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


class AuditLogger:
    """Manages file log serialization followed by database persistence of the file path."""

    def __init__(self):
        self.save_file_service = SaveFileService()
        self.lead_repository = LeadRepository()

    async def audit_logs(self, lead_audit: dict):
        try:
            file_path = await self.save_file_service.save_lead_payload_to_file(lead_audit)

            if file_path and lead_audit.get('LeadId', 0) > 0:
                audit_model = {
                    "AuditPath": file_path,
                    "CrmId": lead_audit.get('LeadId'),
                    "EncryptedRequest": lead_audit.get('EncryptedRequest', ''),
                    "EncryptedResponse": lead_audit.get('EncryptedResponse', ''),
                    "PlainRequest": lead_audit.get('PlainRequest', ''),
                    "PlainResponse": lead_audit.get('PlainResponse', '')
                }
                await self.lead_repository.save_audit_logs(audit_model)
            else:
                logger.warning(
                    f"Payload file path is empty or LeadId is zero. LeadId: {lead_audit.get('LeadId')}"
                )
        except Exception as ex:
            logger.exception(f"Failed to save payload or audit log. LeadId: {lead_audit.get('LeadId')}")


class MasterUseCase:
    """Usecase to query master data like branch lists."""

    def __init__(self):
        self.branch_service = BranchLookupService()

    async def get_branches(self, district_id: int) -> dict:
        branches = self.branch_service.get_branches_by_district_id(district_id)
        if not branches:
            branches = self.branch_service.get_all_branches()
        branch_list = [
            {
                "BranchId": b.get("branch_id"),
                "BranchName": b.get("branch_name"),
                "BranchCode": b.get("branch_code")
            }
            for b in branches
        ]
        if not branch_list:
            return {
                "StatusCode": 400,
                "Message": "No Data Found",
                "Data": []
            }
        return {
            "StatusCode": 200,
            "Message": "Data Found",
            "Data": branch_list
        }

    def get_branches_by_pincode(self, pincode: str) -> dict:
        branches = self.branch_service.get_branches_by_pincode(pincode)
        branch_list = [
            {
                "branch_code": b.get("branch_code"),
                "branch_name": b.get("branch_name")
            }
            for b in branches
        ]
        if not branch_list:
            return {
                "StatusCode": 404,
                "Message": "No branches found for the given pincode",
                "Data": []
            }
        return {
            "StatusCode": 200,
            "Message": "Branches fetched successfully",
            "Data": branch_list
        }


class CreateBajajFinServoLeadUseCase:
    """Core business logic for validating, encrypting, dispatching, and auditing Lead creation."""

    def __init__(self, lead_type_config_provider=None):
        self.lead_repository = LeadRepository()
        self.api_client = BajajFinServoApiClient()
        self.token_service = TokenService()
        self.audit_logger = AuditLogger()
        self.branch_service = BranchLookupService()
        self.lead_type_config_provider = lead_type_config_provider or LeadTypeConfigurationProvider()
        self.config = settings.BAJAJ_CONFIG
        self.val_config = settings.BAJAJ_VALIDATION

    def _build_bajaj_request(self, request_data: dict, pincode: str, lead_type_config) -> dict:
        now_str = datetime.now().strftime(self.config.get('LEAD_DATE_FORMAT', '%Y-%m-%d %H:%M:%S'))

        full_name = request_data.get('FullName', '').strip()
        first_name = ''
        last_name = ''
        if full_name:
            parts = full_name.split()
            first_name = parts[0]
            last_name = parts[-1] if len(parts) > 1 else ''

        lead_details = {
            "lead_id": None,
            "interest_repayment_frequency": "",
            "interest_repayment": "",
            "date_of_birth": "",
            "pan": "",
            "branch_name": "",
            "branck_address": "",
            "gold_loan_officer_name": "",
            "gold_loan_officer_mobile": "",
            "preferred_payment_mode": "",
            "cash_disbursement_required": "",
            "bank_transfer_required": "",
            "cash_and_bank_transfer_required": "",
            "loan_required_in_cash": "",
            "loan_required_in_bank": "",
            "bank_account_no": "",
            "ifsc": "",
            "bank_name": "",
            "bank_branch_name": "",
            "kyc_completion_status": "",
            "kyc_method_used": "",
            "kyc_name": "",
            "kyc_address": "",
            "kyc_dob": "",
            "kyc_city": "",
            "kyc_state": "",
            "kyc_pincode": "",
            "kyc_photo": "",
            "total_loan_amount_bt": "",
            "rate_of_interest_bt": "",
            "gold_weight_bt": "",
            "name_of_loan_provider_bt": "",
            "gdr_upload_status_bt": "",
            "gdr_image_bt": "",
            "loan_amount_with_bfl_bt": "",
            "monthly_interest_with_bfl_bt": "",
            "potential_annual_interest_savings_bt": "",
            "extra_amount_for_same_gold_weight_bt": "",
            "eligibility_for_reward_for_completing_journey_bt": "",
            "eligibility_for_reward_for_completing_journey_additional_info": "",
            "share_jewellery_details_completion": "",
            "ornament_details": "",
            "customer_is_rsl_rpl_reject": "",
            "lead_req_date_time": "",
            "dynamicinfo": "",
            "gl_loan_existing": "",
            "docDtl": "",
            "docName": "",
            "docType": "",
            "docCode": "",
            "account_type": ""
        }

        return {
            "lead_generation_datetime": now_str,
            "mobile": request_data.get('MobileNo'),
            "lead_required_amount": str(request_data.get('LoanAmount')),
            "total_gold_weight": "",
            "interest_repayment_frequency": "",
            "tenure": "",
            "interest_repayment": "",
            "rate_of_interest": "",
            "disposition_time": "",
            "first_name": first_name,
            "last_name": last_name,
            "tokenno": "",
            "product": lead_type_config.product,
            "lead_type": self.config.get('LEAD_TYPE'),
            "emp_id": "",
            "disposition_type": "",
            "lead_source": lead_type_config.lead_source,
            "lead_origin": lead_type_config.lead_origin,
            "employement_type": "",
            "employement_subtype": "",
            "journey_name": self.config.get('JOURNEY_NAME'),
            "competitor_name": "",
            "competitor_loan_amount": "",
            "final_loan_amount": "",
            "lead_remark": "",
            "lead_channel": lead_type_config.lead_channel,
            "lead_status": "",
            "emp_role": "",
            "emp_adid": "",
            "emp_name": "",
            "alt_mobile": "",
            "branch_id": "",
            "followup": str(self.config.get('FOLLOW_UP')).lower(),
            "eventCode": "",
            "src": lead_type_config.src,
            "internal_src": self.config.get('INTERNAL_SOURCE'),
            "pincode": pincode,
            "dsc_code": self.config.get('DSC_CODE'),
            "sub_code": self.config.get('SUB_CODE'),
            "subsub_code": "",
            "referral_id": self.config.get('REFERRAL_ID'),
            "referral_business": "",
            "referral_partner": lead_type_config.referral_partner,
            "lead_details_3in1": lead_details
        }

    async def execute(self, request_data: dict) -> dict:
        encrypted_request = ""
        encrypted_response_text = ""
        plain_response_json = "{}"
        is_api_success = False
        lead_id = 0
        access_token = ""

        lead_type_config = self.lead_type_config_provider.get_configuration(request_data.get('Type'))

        # ---------------------------------------------------------------
        # Step 1: Branch Lookup
        # ---------------------------------------------------------------
        logger.info("Step 1: Branch Lookup - Starting")
        branch_identifier = request_data.get('Branch')
        logger.debug(f"Branch lookup input: {branch_identifier!r}")

        # The overall usecase is async; DB-backed lookup is synchronous. Run
        # the synchronous branch lookup in a thread to avoid Django's
        # SynchronousOnlyOperation when called from async context.
        from asgiref.sync import sync_to_async
        try:
            branch = await sync_to_async(self.branch_service.get_branch)(branch_identifier)
            logger.debug(f"Branch lookup result: {branch}")
        except Exception as ex:
            logger.exception(f"Exception during branch lookup for {branch_identifier!r}: {ex}")
            branch = None

        if not branch:
            raise BajajFinServoApiException(
                "Branch Not Found",
                status.HTTP_400_BAD_REQUEST
            )
        logger.info(f"Branch found: {request_data.get('Branch')}")

        pincode = branch.get("pincode", "")
        final_request = self._build_bajaj_request(request_data, pincode, lead_type_config)
        plain_request_json = json.dumps(final_request)

        lead_insert_model = {
            "FullName": request_data.get('FullName'),
            "PinCode": pincode,
            "MobileNo": request_data.get('MobileNo'),
            "SBOState": request_data.get('SBOState'),
            "SBODistrict": request_data.get('SBODistrict'),
            "Branch": request_data.get('Branch'),
            "LeadStatus": "2",
            "LoanAmount": request_data.get('LoanAmount'),
            "ApiMessage": "",
            "CrmId": None
        }

        try:
            # ---------------------------------------------------------------
            # Step 2: Encryption (with bypass option)
            # ---------------------------------------------------------------
            logger.info("Step 2: Encryption - Starting")
            shared_key = self.config.get('SHARED_SECRET_KEY')
            shared_iv = self.config.get('SHARED_SECRET_IV')

            if BYPASS_ENCRYPTION:
                logger.warning("BYPASS_ENCRYPTION is enabled - skipping encryption, using plain payload")
                encrypted_request = plain_request_json
            else:
                try:
                    logger.info(f"SHARED_SECRET_KEY length: {len(shared_key) if shared_key else 0}")
                    logger.info(f"SHARED_SECRET_IV length: {len(shared_iv) if shared_iv else 0}")
                    logger.info(f"SHARED_SECRET_IV value: [{shared_iv}]")
                    logger.info("Encryption About To Start")
                    encrypted_request = AESCryptoUtility.encrypt(plain_request_json, shared_key, shared_iv)
                    logger.info("Encryption completed successfully")
                except Exception as ex:
                    logger.exception("Encryption of the API Request failed")
                    raise BajajFinServoApiException(f"Encryption of the API Request failed. {str(ex)}")

            # ---------------------------------------------------------------
            # Step 3: Token API
            # ---------------------------------------------------------------
            logger.info("Step 3: Token API Call - Starting")
            try:
                access_token = await self.token_service.get_access_token()
                logger.info("Token API - Token obtained successfully")
                logger.info(f"Token - masked: {access_token[:10]}...{access_token[-5:] if len(access_token) > 15 else ''}")
            except TokenApiException as ex:
                logger.exception("Token API execution failed")
                raise
            except Exception as ex:
                logger.exception("Token API execution failed")
                raise TokenApiException(str(ex), 500, None)

            # ---------------------------------------------------------------
            # Step 4: Lead API Call
            # ---------------------------------------------------------------
            logger.info("Step 4: Lead API Call - Starting")
            encrypted_response_text = await self.api_client.create_lead(
                encrypted_request,
                access_token,
                source_header=lead_type_config.header_source
            )
            logger.info("Lead API Call - Response received")

            # ---------------------------------------------------------------
            # Step 5: Response Decryption
            # ---------------------------------------------------------------
            logger.info("Step 5: Response Decryption - Starting")
            try:
                if BYPASS_ENCRYPTION:
                    plain_response = encrypted_response_text
                else:
                    plain_response = AESCryptoUtility.decrypt(encrypted_response_text, shared_key, shared_iv)
                try:
                    outer_val = json.loads(plain_response)
                    if isinstance(outer_val, str):
                        response_object = json.loads(outer_val)
                    else:
                        response_object = outer_val
                except Exception:
                    response_object = json.loads(plain_response)

                plain_response_json = json.dumps(response_object)
                logger.info("Response decrypted successfully")
            except Exception as ex:
                lead_insert_model["ApiMessage"] = "Decryption failed"
                logger.exception("Decryption of API Response failed")
                raise BajajFinServoApiException(f"Decryption of API Response failed. {str(ex)}")

            is_api_success = True

            # ---------------------------------------------------------------
            # Step 6: Map Result
            # ---------------------------------------------------------------
            logger.info("Step 6: Mapping Result - Starting")
            mapped_result = self._map_lead_result(response_object, request_data.get('MobileNo'))

            lead_insert_model["ApiMessage"] = mapped_result.get('Message')
            lead_status_str = mapped_result.get('Status')
            if lead_status_str == 'Success':
                lead_insert_model["LeadStatus"] = "1"
            elif lead_status_str == 'Duplicate':
                lead_insert_model["LeadStatus"] = "3"
            elif lead_status_str == 'Rejected':
                lead_insert_model["LeadStatus"] = "4"
            else:
                lead_insert_model["LeadStatus"] = "2"

            lead_insert_model["CrmId"] = mapped_result.get('LeadReference')
            logger.info(f"UseCase execute complete: status={mapped_result.get('Status')}")
            return mapped_result

        except BajajFinServoApiException as ex:
            logger.error(f"BajajFinServoApiException: {ex.message} (status={ex.status_code})")
            lead_insert_model["ApiMessage"] = ex.message
            lead_insert_model["LeadStatus"] = "2"
            return self._failure_result(ex.status_code, ex.message)
        except TokenApiException as ex:
            logger.error(f"TokenApiException: {ex.message} (status={ex.status_code})")
            lead_insert_model["ApiMessage"] = ex.message
            lead_insert_model["LeadStatus"] = "2"
            return self._failure_result(ex.status_code, ex.message)
        except Exception as ex:
            logger.exception("Unhandled error in UseCase execution")
            lead_insert_model["ApiMessage"] = "Internal server error"
            lead_insert_model["LeadStatus"] = "2"
            return self._failure_result(500, "Internal server error")
        finally:
            try:
                db_res = await self.lead_repository.save_crm_details(lead_insert_model)
                if db_res.get('ResponseCode') == 200 and db_res.get('CmsId') > 0:
                    lead_id = db_res.get('CmsId')

                audit_payload = {
                    "LeadId": lead_id,
                    "EncryptedRequest": encrypted_request,
                    "EncryptedResponse": encrypted_response_text,
                    "PlainRequest": plain_request_json,
                    "PlainResponse": plain_response_json
                }
                await self.audit_logger.audit_logs(audit_payload)
            except Exception as ex:
                logger.error(f"Audit final block failed: {str(ex)}")

    def _map_lead_result(self, response_data: dict, mobile_no: str) -> dict:
        default_fail_msg = "Technical failure occurred"
        status_code = response_data.get('statusCode', 500)
        message = response_data.get('message', '')
        data = response_data.get('data') or {}

        if status_code in [200]:
            remarks = data.get('remarks') or message or ''
            partner_status = (data.get('status') or '').lower()

            is_rejected = 'reject' in partner_status or 'reject' in remarks.lower()

            if is_rejected:
                is_duplicate = data.get('lead_id') is not None or "already exists" in remarks.lower()

                if is_duplicate:
                    lead_reference_id = str(data.get('lead_id') or '')
                    msg_format = "There is already an existing Lead No: {0} for mobile number {1}."
                    return {
                        "StatusCode": status_code,
                        "Message": msg_format.format(lead_reference_id, mobile_no),
                        "Status": "Duplicate",
                        "LeadReference": lead_reference_id,
                        "Remarks": remarks
                    }
                return {
                    "StatusCode": status_code,
                    "Message": remarks,
                    "Status": "Rejected",
                    "LeadReference": None,
                    "Remarks": remarks
                }

            return {
                "StatusCode": status_code,
                "Message": message,
                "Status": "Success",
                "LeadReference": str(data.get('lead_id') or ''),
                "Remarks": remarks
            }

        status_descriptions = {
            400: "Invalid Request / Bad Request",
            500: "Internal Server Error",
            4001: "Encryption-decryption failed due to invalid request",
            5001: "Function failure",
            5003: "Incorrect JSON"
        }

        description = status_descriptions.get(status_code, "Unexpected response received from partner")
        err_msg = message or data.get('remarks') or description

        return {
            "StatusCode": status_code,
            "Message": err_msg,
            "Status": "Failed",
            "LeadReference": None,
            "Remarks": ""
        }

    def _failure_result(self, code: int, message: str) -> dict:
        return {
            "StatusCode": code,
            "Message": message,
            "Status": "Failed",
            "LeadReference": None,
            "Remarks": ""
        }
