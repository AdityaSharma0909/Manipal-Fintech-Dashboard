import logging
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from utility.error_handler import HttpErrors
from onboarding_v2.serializers.loan_punch import LoanPunchSerializer, SingleLoanPunchSerializer
from onboarding_v2.models import ApplicationV2, LoanPunchV2
from onboarding_v2.constants import ApplicationStatus

logger = logging.getLogger(__name__)

class LoanPunchView(APIView):
    """
    Handle loan punching for applications. Supports single or multiple loans.
    """
    @extend_schema(
        tags=["Onboarding V2"],
        summary="Get loan punch entries for an application",
        description="Retrieve existing loan punch records for a given application ID.",
        parameters=[
            OpenApiParameter(
                name="Application ID",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Application ID. Example: MPAGL0183",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="LoanPunchGetResponse",
                    fields={
                        "status": serializers.CharField(default="success"),
                        "data": inline_serializer(
                            name="LoanPunchGetData",
                            fields={
                                "application_id": serializers.CharField(),
                                "loans": SingleLoanPunchSerializer(many=True),
                            },
                        ),
                    },
                ),
            ),
            404: OpenApiResponse(description="Application not found."),
        },
    )
    def get(self, request):
        application_id = request.query_params.get("application_id")
        if not application_id:
            return HttpResponse.BadRequest("application_id is required")
            
        try:
            application = ApplicationV2.objects.get(application_id=application_id)
        except ApplicationV2.DoesNotExist:
            return HttpResponse.NotFound("Application not found")
            
        punched_loans = application.punched_loans.all()
        return HttpResponse.Success({
            "application_id": application_id,
            "loans": SingleLoanPunchSerializer(punched_loans, many=True).data
        })

    @extend_schema(
        tags=["Onboarding V2"],
        operation_id="loan_punch_create",
        summary="Create loan punch entries for an application",
        description=(
            "Accepts one or more loan punch records for a single application. "
            "All loans in the request must belong to the same bank. "
            "Set is_submit to False for Save and Exit functionality. "
            "When is_submit is True (default), the following fields are mandatory for each loan: "
            "bank_name, approved_tenure, disbursed_amount, rate_of_interest, "
            "loan_account_number, sanctioned_amount, loan_opening_date. "
            "For GOLD_LOAN applications, gross_weight and net_weight are also mandatory. "
            "Final Bajaj submissions (including BT) also require loan_account_document "
            "and product_approval_screenshot URLs. These fields are optional for other banks."
        ),
        request=LoanPunchSerializer,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name="LoanPunchSuccessResponse",
                    fields={
                        "status": serializers.CharField(default="success"),
                        "data": inline_serializer(
                            name="LoanPunchSuccessData",
                            fields={
                                "message": serializers.CharField(),
                                "application_id": serializers.CharField(),
                                "status": serializers.CharField(),
                                "loans": SingleLoanPunchSerializer(many=True),
                            },
                        ),
                    },
                ),
                description="Loan punching completed successfully.",
            ),
            400: OpenApiResponse(description="Validation error in request payload."),
            500: OpenApiResponse(description="Unexpected server error while punching loan."),
        },
        examples=[
            OpenApiExample(
                name="Save and Exit Payload",
                value={
                    "application_id": "MPAGL0183",
                    "is_submit": False,
                    "agent_id": "A123",
                    "agent_name": "Agent Smith",
                    "loans": [
                        {
                            "approval_status": "APPROVED",
                            "bank_name": "HDFC BANK",
                            "crm_id": "CRM987654",
                            "is_agriculture": False,
                            "loan_account_number": "5010012345",
                            "loan_account_document": "https://storage.example.com/lan-document.jpg",
                            "product_approval_screenshot": "https://storage.example.com/product-approval.jpg",
                            "loan_opening_date": "2024-03-25",
                            "sanctioned_amount": 50000.00,
                            "approved_tenure": 12,
                            "disbursed_amount": 45000.00,
                            "rate_of_interest": 10.5,
                            "gross_weight": 15.500,
                            "net_weight": 14.200,
                            "is_customer_kit_gifted": True,
                            "remarks": "Partially filled info",
                        }
                    ],
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Rejected Loan Payload",
                value={
                    "application_id": "MPAGL0183",
                    "agent_id": "A123",
                    "agent_name": "Agent Smith",
                    "loans": [
                        {
                            "approval_status": "REJECTED",
                            "rejection_reason": "Low Credit Score",
                            "remarks": "Customer does not meet criteria",
                            "bank_name": "Axis Bank",
                        }
                    ],
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Approved Loan Payload",
                value={
                    "application_id": "MPAGL0183",
                    "loans": [
                        {
                            "approval_status": "APPROVED",
                            "bank_name": "HDFC BANK",
                            "crm_id": "CRM987654",
                            "is_agriculture": False,
                            "loan_account_number": "5010012345",
                            "loan_opening_date": "2024-03-25",
                            "sanctioned_amount": 50000.00,
                            "approved_tenure": 12,
                            "disbursed_amount": 45000.00,
                            "rate_of_interest": 10.5,
                            "gross_weight": 15.500,
                            "net_weight": 14.200,
                            "is_customer_kit_gifted": True,
                            "is_bank_changed": True,
                            "new_bank_name": "New Bank",
                            "new_bank_state": "Karnataka",
                            "new_bank_district": "Bangalore",
                            "new_bank_branch": "HSR Layout",
                            "remarks": "Loan approved after successful verification",
                            "kit_images": [
                                "https://storage.example.com/kit1.jpg",
                                "https://storage.example.com/kit2.jpg",
                            ],
                            "loan_doc_images": [
                                "https://storage.example.com/doc1.pdf",
                            ],
                        }
                    ],
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        logger.info("Loan punching request | payload=%s", request.data)
        
        serializer = LoanPunchSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return HttpResponse.BadRequest(serializer.errors)
            
        try:
            is_submit = serializer.validated_data.get("is_submit", True)
            punched_loans = serializer.save()
            
            application = serializer.validated_data["application_id"]
            
            if is_submit:
                # Update application status if primary loan is approved/rejected
                primary_loan = punched_loans[0]
                
                if primary_loan.approval_status == LoanPunchV2.ApprovalStatus.APPROVED:
                    application.status = ApplicationStatus.LOAN_STATUS_UPDATED
                    application.save()
                elif primary_loan.approval_status == LoanPunchV2.ApprovalStatus.REJECTED:
                    application.status = ApplicationStatus.REJECTED
                    application.save()
                elif primary_loan.approval_status == LoanPunchV2.ApprovalStatus.CHANGE_BANK or primary_loan.is_bank_changed:
                    # Update application's lending partner if changed
                    new_bank = primary_loan.new_bank_name if primary_loan.is_bank_changed else primary_loan.bank_name
                    if new_bank:
                        # Try to find a matching LendingPartner choice
                        from onboarding_v2.constants import LendingPartner
                        for choice in LendingPartner.choices:
                            if choice[1].upper() in new_bank.upper() or new_bank.upper() in choice[1].upper():
                                application.lending_partner = choice[0]
                                break
                    print(f"Updated lending partner to {application.lending_partner} for bank {new_bank}")
                    application.status = ApplicationStatus.CORRECTION
                    application.save()
            
            if not is_submit:
                message = "Loan(s) saved successfully"
            else:
                primary_loan = punched_loans[0]
                if primary_loan.approval_status == LoanPunchV2.ApprovalStatus.REJECTED:
                    message = "Loan rejected "
                elif primary_loan.approval_status == LoanPunchV2.ApprovalStatus.CHANGE_BANK or primary_loan.is_bank_changed:
                    message = "Loan(s) punched successfully"
                else:
                    message = "Loan(s) punched successfully"

            response_data = {
                 "message": message,
                 "application_id": application.application_id,
                 "status": application.status,
                 "loans": SingleLoanPunchSerializer(punched_loans, many=True).data
             }
            
            return HttpResponse.Success(response_data)
            
        except Exception as exc:
            logger.exception("Loan punching failed")
            return HttpErrors.InternalServerError(f"Failed to punch loan: {str(exc)}")
