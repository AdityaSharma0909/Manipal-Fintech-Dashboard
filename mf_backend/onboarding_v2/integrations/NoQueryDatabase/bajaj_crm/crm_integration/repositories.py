import logging
from crm_integration.models import Lead, LeadAudit, LeadStatusChoices
from crm_integration.services.branch_lookup_service import BranchLookupService

logger = logging.getLogger(__name__)


class LeadRepository:
    """

    Orchestrates all lead inserts, updates, and audit persistence.
    """

    async def get_request_data_async(self, branch_id: str) -> dict:
        """Fetches branch pincode and details from JSON file."""
        try:
            branch_service = BranchLookupService()
            branch = branch_service.get_branch(branch_id)
            
            if not branch:
                return {
                    "ResponseCode": 400,
                    "ResponseMessage": "Branch Not Found",
                    "Pincode": "",
                    "BranchCode": ""
                }

            return {
                "ResponseCode": 200,
                "ResponseMessage": "Success",
                "Pincode": branch.get("pincode", ""),
                "BranchCode": branch.get("branch_code", "")
            }
        except Exception as ex:
            logger.error(f"Error executing get_request_data_async for branch {branch_id}: {str(ex)}")
            return {
                "ResponseCode": 500,
                "ResponseMessage": f"Internal server error: {str(ex)}",
                "Pincode": "",
                "BranchCode": ""
            }

    async def save_crm_details(self, insert_model: dict) -> dict:
        """Saves lead details to the database."""
        from asgiref.sync import sync_to_async

        @sync_to_async
        def insert_lead():
            try:
                # Map LeadStatus code strings to model choices
                status_text = insert_model.get('LeadStatus', 'Failed')
                # If status is passed as a number representation or text, normalize it.
                if status_text == "1":
                    status_val = LeadStatusChoices.SUCCESS
                elif status_text == "2":
                    status_val = LeadStatusChoices.FAILED
                elif status_text == "3":
                    status_val = LeadStatusChoices.DUPLICATE
                elif status_text == "4":
                    status_val = LeadStatusChoices.REJECTED
                else:
                    status_val = status_text

                lead = Lead.objects.create(
                    full_name=insert_model.get('FullName'),
                    mobile_no=insert_model.get('MobileNo'),
                    pincode=insert_model.get('PinCode'),
                    loan_amount=insert_model.get('LoanAmount'),
                    crm_id=insert_model.get('CrmId'),
                    api_message=insert_model.get('ApiMessage'),
                    state=insert_model.get('SBOState') or '',
                    district=insert_model.get('SBODistrict') or '',
                    branch=insert_model.get('Branch') or '',
                    lead_status=status_val
                )
                return {
                    "ResponseCode": 200,
                    "ResponseMessage": "Success",
                    "CmsId": lead.id
                }
            except Exception as ex:
                logger.exception("Failed to insert lead details to DB")
                return {
                    "ResponseCode": 500,
                    "ResponseMessage": f"Database insertion failed: {str(ex)}",
                    "CmsId": 0
                }

        return await insert_lead()

    async def save_audit_logs(self, audit_model: dict) -> dict:
        """Saves file log details and correlates them to a lead record."""
        from asgiref.sync import sync_to_async

        @sync_to_async
        def write_audit():
            try:
                lead_id = audit_model.get('CrmId')
                file_path = audit_model.get('AuditPath')
                
                # Fetch request/response values stored temporarily in thread local or passed
                # C# saves the audit details, we create the Audit record linking it to Lead.
                lead = Lead.objects.filter(id=lead_id).first()
                
                # C# passes LeadAudit details. We populate plain/encrypted texts from the logged file if needed,
                # or read from audit_model if passed. C# stores these details inside the file on disk.
                # Let's populate the audit record.
                
                LeadAudit.objects.create(
                    lead=lead,
                    file_path=file_path,
                    encrypted_request=audit_model.get('EncryptedRequest', ''),
                    encrypted_response=audit_model.get('EncryptedResponse', ''),
                    plain_request=audit_model.get('PlainRequest', ''),
                    plain_response=audit_model.get('PlainResponse', '')
                )
                return {
                    "ResponseCode": 200,
                    "ResponseMessage": "Success"
                }
            except Exception as ex:
                logger.exception("Failed to save audit logs to DB")
                return {
                    "ResponseCode": 500,
                    "ResponseMessage": f"Audit logging failed: {str(ex)}"
                }

        return await write_audit()
