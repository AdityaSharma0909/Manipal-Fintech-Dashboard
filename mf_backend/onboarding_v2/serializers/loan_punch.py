from rest_framework import serializers
from onboarding_v2.models import LoanPunchV2, ApplicationV2, LeadV2
from onboarding_v2.constants import ProductSubCategory

class SingleLoanPunchSerializer(serializers.ModelSerializer):
    kit_images = serializers.ListField(child=serializers.URLField(), required=False, default=list)
    loan_doc_images = serializers.ListField(child=serializers.URLField(), required=False, default=list)

    class Meta:
        model = LoanPunchV2
        fields = [
            "approval_status",
            "bank_name",
            "crm_id",
            "is_agriculture",
            "loan_account_number",
            "loan_account_document",
            "product_approval_screenshot",
            "loan_opening_date",
            "sanctioned_amount",
            "approved_tenure",
            "disbursed_amount",
            "rate_of_interest",
            "gross_weight",
            "net_weight",
            "is_customer_kit_gifted",
            "is_bank_changed",
            "new_bank_name",
            "new_bank_state",
            "new_bank_district",
            "new_bank_branch",
            "rejection_reason",
            "agent_id",
            "agent_name",
            "remarks",
            "kit_images",
            "loan_doc_images",
        ]
        extra_kwargs = {
            "loan_account_number": {
                "validators": [],
            }
        }


    def to_representation(self, instance):
        ret = super().to_representation(instance)
        metadata = instance.metadata or {}
        ret["kit_images"] = metadata.get("kit_images", [])
        ret["loan_doc_images"] = metadata.get("loan_doc_images", [])
        return ret

    @staticmethod
    def _validate_loan_account_number_format(loan_acc, is_gold_loan):
        if not loan_acc:
            return

        # if is_gold_loan:
        #     if not loan_acc.isdigit():
        #         raise serializers.ValidationError(
        #             {"loan_account_number": "Loan account number must contain only digits"}
        #         )
        #     return

        # if not loan_acc.isalnum():
        #     raise serializers.ValidationError(
        #         {"loan_account_number": "Loan account number must be alphanumeric"}
        #     )

    @staticmethod
    def _normalize_bank_name(value):
        if value is None:
            return None
        return value.strip().upper()

    def validate(self, data):
        is_submit = self.context.get("is_submit", True)
        is_gold_loan = self.context.get("is_gold_loan", False)

        # CRM ID Validations (Checked regardless of is_submit if crm_id is provided)
        crm_id = data.get("crm_id")
        if crm_id:
            # 1. The same CRM ID should not be used in multiple loan punchings.
            application = self.context.get("application")
            existing_punch = LoanPunchV2.objects.filter(crm_id=crm_id)
            if application:
                existing_punch = existing_punch.exclude(application=application)
            
            if existing_punch.exists():
                raise serializers.ValidationError({"crm_id": f"CRM ID {crm_id} is already used in another loan punching."})

            # 2. CRM ID must exist in the system (LeadV2 as BankLeadID)
            lead = LeadV2.objects.filter(BankLeadID=crm_id).first()
            if not lead:
                raise serializers.ValidationError({"crm_id": f"CRM ID {crm_id} does not exist in the system as a Bank Lead ID."})

            # 3. CRM ID and Punched By validation
            # The SO (Sales Officer) who created the bank lead must be the same user performing the loan punching.
            request = self.context.get("request")
            if request and request.user:
                if lead.created_by != request.user:
                    raise serializers.ValidationError({"crm_id": f"The user performing loan punching does not match the creator of lead {crm_id}."})

            # 4. Lead bank name and loan punch bank name must be the same.
            # For bank-change cases, CRM ID belongs to the new/target bank.
            bank_field = "new_bank_name" if data.get("is_bank_changed") else "bank_name"
            bank_name = data.get(bank_field)
            if lead.bank and bank_name:
                if self._normalize_bank_name(lead.bank) != self._normalize_bank_name(bank_name):
                    raise serializers.ValidationError(
                        {bank_field: f"The bank name '{bank_name}' does not match the lead bank name '{lead.bank}' associated with CRM ID {crm_id}."}
                    )

        if not is_submit:
            # Skip strict validations for Save and Exit
            # Still check loan account number format if provided
            loan_acc = data.get("loan_account_number", "")
            self._validate_loan_account_number_format(loan_acc, is_gold_loan)
            return data

        # When is_submit is True, these fields are mandatory
        mandatory_fields = [
            "bank_name", "approved_tenure", "disbursed_amount", "rate_of_interest",
            "loan_account_number", "sanctioned_amount",
            "loan_opening_date"
        ]
        if is_gold_loan:
            mandatory_fields.extend(["gross_weight", "net_weight"])
        
        # Only check these if approval_status is not REJECTED
        approval_status = data.get("approval_status")
        if approval_status != LoanPunchV2.ApprovalStatus.REJECTED:
            for field in mandatory_fields:
                val = data.get(field)
                if val is None or val == "":
                    raise serializers.ValidationError({field: f"{field.replace('_', ' ').capitalize()} is mandatory and cannot be null or empty for submission"})

        # 1. Bank Change Validation
        if data.get("is_bank_changed"):
            required_bank_fields = ["new_bank_name"]
            if is_gold_loan:
                required_bank_fields.extend(["new_bank_state", "new_bank_district", "new_bank_branch"])
            for field in required_bank_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: f"{field.replace('_', ' ').capitalize()} is mandatory when bank is changed"})

        # 2. Loan Account Number Validation
        # Skip validation if status is Reject and loan_account_number is not provided
        approval_status = data.get("approval_status")
        loan_acc = data.get("loan_account_number", "")
        
        if approval_status == LoanPunchV2.ApprovalStatus.REJECTED and not loan_acc:
            # If rejected, we might not have loan details
            pass
        else:
            # if "ICICI" in bank:
            #     if not (9 <= length <= 12):
            #         raise serializers.ValidationError({"loan_account_number": f"ICICI Bank loan account number must be 9 to 12 digits (got {length})"})
            # elif "HDFC" in bank:
            #     if length not in [8, 10]:
            #         raise serializers.ValidationError({"loan_account_number": f"HDFC Bank loan account number must be 8 or 10 digits (got {length})"})
            # elif "RBL" in bank:
            #     if length != 12:
            #         raise serializers.ValidationError({"loan_account_number": f"RBL Bank loan account number must be 12 digits (got {length})"})
            # elif "AXIS" in bank:
            #     if length != 15:
            #         raise serializers.ValidationError({"loan_account_number": f"Axis Bank loan account number must be 15 digits (got {length})"})
            # elif "DBS" in bank:
            #     if length != 16:
            #         raise serializers.ValidationError({"loan_account_number": f"DBS Bank loan account number must be 16 digits (got {length})"})
            # elif "KOTAK" in bank:
            #     if length != 7:
            #         raise serializers.ValidationError({"loan_account_number": f"Kotak Bank loan account number must be 7 digits (got {length})"})
            # else:
            #     if not (5 <= length <= 18):
            #         raise serializers.ValidationError({"loan_account_number": f"Loan account number must be between 5 and 18 digits (got {length})"})
            
            self._validate_loan_account_number_format(loan_acc, is_gold_loan)

        # 3. Amount & Weight Checks
        sanctioned = data.get("sanctioned_amount")
        disbursed = data.get("disbursed_amount")
        
        if approval_status != LoanPunchV2.ApprovalStatus.REJECTED:
            # if disbursed and sanctioned and disbursed > sanctioned:
            #     raise serializers.ValidationError({"disbursed_amount": "Disbursed amount cannot be greater than sanctioned amount"})
            
            if data.get("net_weight") and data.get("gross_weight") and data.get("net_weight") > data.get("gross_weight"):
                raise serializers.ValidationError({"net_weight": "Net weight cannot be greater than gross weight"})
            
        # 4. CRM ID requirement (made optional as per user request)
        # if approval_status != LoanPunchV2.ApprovalStatus.REJECTED:
        #     if any(b in bank for b in ["AXIS", "HDFC", "ICICI"]) and not data.get("crm_id"):
        #          raise serializers.ValidationError({"crm_id": f"CRM ID is mandatory for {bank}"})
             
        # 5. Rejection reason requirement
        if approval_status == LoanPunchV2.ApprovalStatus.REJECTED and not data.get("rejection_reason"):
            raise serializers.ValidationError({"rejection_reason": "Rejection reason is mandatory when status is Reject"})
            
        return data

class LoanPunchSerializer(serializers.Serializer):
    application_id = serializers.CharField()
    loans = SingleLoanPunchSerializer(many=True)
    is_submit = serializers.BooleanField(default=True, required=False)
    agent_id = serializers.CharField(required=False, allow_null=True)
    agent_name = serializers.CharField(required=False, allow_null=True)

    @staticmethod
    def _normalize_bank_name(value):
        if value is None:
            return None
        return value.strip().upper()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pass is_submit to nested serializer context if it's in the data
        is_submit = True
        is_gold_loan = False
        self._application_from_init = None
        if hasattr(self, "initial_data") and self.initial_data:
            is_submit = self.initial_data.get("is_submit")
            if is_submit is None:
                 is_submit = True # Default to true if null
            application_id = self.initial_data.get("application_id")
            if application_id:
                self._application_from_init = (
                    ApplicationV2.objects.select_related("lead")
                    .filter(application_id=application_id)
                    .first()
                )
                if (
                    self._application_from_init
                    and self._application_from_init.lead
                    and self._application_from_init.lead.product_subcategory == ProductSubCategory.GOLD_LOAN
                ):
                    is_gold_loan = True
        
        self.context["is_submit"] = is_submit
        self.context["is_gold_loan"] = is_gold_loan

    def validate_application_id(self, value):
        if self._application_from_init and self._application_from_init.application_id == value:
            application = self._application_from_init
        else:
            try:
                application = ApplicationV2.objects.select_related("lead").get(application_id=value)
            except ApplicationV2.DoesNotExist:
                raise serializers.ValidationError("Application not found")

        self.context["application"] = application
        self.context["is_gold_loan"] = bool(
            application.lead and application.lead.product_subcategory == ProductSubCategory.GOLD_LOAN
        )
        return application
        
    def validate(self, data):
        application_id = data.get("application_id")
        if not application_id:
            raise serializers.ValidationError({"application_id": "Application ID cannot be null or empty"})
            
        loans = data.get("loans", [])
        if loans is None or not loans:
            raise serializers.ValidationError({"loans": "Loans list cannot be null or empty"})

        # Check for duplicate loan account numbers within the request
        loan_accs = [
            str(loan.get("loan_account_number")).strip()
            for loan in loans
            if loan.get("loan_account_number")
        ]
        if len(loan_accs) != len(set(loan_accs)):
            raise serializers.ValidationError(
                {"loan_account_number": "The entered Loan Account Number is already in use. Please enter a different Loan Account Number."}
            )

        # Check if any loan account number is already used in another application
        if loan_accs:
            application = self.context.get("application")
            existing_punches = LoanPunchV2.objects.filter(loan_account_number__in=loan_accs)
            if application:
                existing_punches = existing_punches.exclude(application=application)
            if existing_punches.exists():
                raise serializers.ValidationError(
                    {"loan_account_number": "The entered Loan Account Number is already in use. Please enter a different Loan Account Number."}
                )
            
        # All loans must have the same bank
        primary_bank = loans[0].get("bank_name")
        normalized_primary_bank = self._normalize_bank_name(primary_bank)
        if not normalized_primary_bank:
            raise serializers.ValidationError({"loans": "Bank name is required for all loans"})

        for loan in loans[1:]:
            normalized_bank_name = self._normalize_bank_name(loan.get("bank_name"))
            if not normalized_bank_name:
                raise serializers.ValidationError({"loans": "Bank name is required for all loans"})
            if normalized_bank_name != normalized_primary_bank:
                raise serializers.ValidationError({"loans": "All loans must belong to the same bank"})

        changed_bank_loans = [loan for loan in loans if loan.get("is_bank_changed")]
        if changed_bank_loans:
            primary_new_bank = changed_bank_loans[0].get("new_bank_name")
            normalized_primary_new_bank = self._normalize_bank_name(primary_new_bank)
            if not normalized_primary_new_bank:
                raise serializers.ValidationError({"new_bank_name": "New bank name is required when bank is changed"})

            for loan in changed_bank_loans[1:]:
                normalized_new_bank_name = self._normalize_bank_name(loan.get("new_bank_name"))
                if not normalized_new_bank_name:
                    raise serializers.ValidationError({"new_bank_name": "New bank name is required when bank is changed"})
                if normalized_new_bank_name != normalized_primary_new_bank:
                    raise serializers.ValidationError({"loans": "All changed loans must belong to the same new bank"})

        return data

    def create(self, validated_data):
        application = validated_data["application_id"]
        loans_data = validated_data["loans"]
        agent_id = validated_data.get("agent_id")
        agent_name = validated_data.get("agent_name")
        
        # Clear existing punched loans for this application to avoid duplicates
        LoanPunchV2.objects.filter(application=application).delete()
        
        punched_loans = []
        for loan_data in loans_data:
            # If agent info is at root but not in loan_data, apply it
            if agent_id and not loan_data.get("agent_id"):
                loan_data["agent_id"] = agent_id
            if agent_name and not loan_data.get("agent_name"):
                loan_data["agent_name"] = agent_name

            kit_images = loan_data.pop("kit_images", [])
            loan_doc_images = loan_data.pop("loan_doc_images", [])
            
            # Store image URLs in metadata for now
            metadata = loan_data.get("metadata", {}) or {}
            metadata["kit_images"] = kit_images
            metadata["loan_doc_images"] = loan_doc_images
            loan_data["metadata"] = metadata
            
            loan = LoanPunchV2.objects.create(application=application, **loan_data)
            punched_loans.append(loan)
            
        return punched_loans
