from django.db import migrations, models
import django.db.models.deletion
import onboarding_v2.models
import uuid


class CreateModelIfNotExists(migrations.CreateModel):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.name)
        if model._meta.db_table in schema_editor.connection.introspection.table_names():
            return
        super().database_forwards(app_label, schema_editor, from_state, to_state)


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0046_alter_applicationdocument_document_type_and_more"),
        ("onboarding_v2", "0048_creditscorerange_and_more"),
    ]

    operations = [
        CreateModelIfNotExists(
            name="CorrectionOnboarding",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "stage",
                    models.CharField(
                        choices=[
                            ("PAN", "Pan"),
                            ("BASIC", "Basic"),
                            ("ADDRESS", "Address"),
                            ("DOCUMENTS", "Documents"),
                            ("PERSONAL", "Personal"),
                            ("ADDRESS_SECONDARY", "AddressSecondary"),
                            ("GOLD", "Gold"),
                            ("PLEDGE_CARD", "Pledge Card"),
                            ("LOAN", "Loan"),
                            ("BANK", "Bank"),
                            ("ADDITIONAL", "Additional"),
                            ("CUSTOMER_VISIT", "Customer Visit"),
                            ("WAIVER", "Waiver"),
                            ("ELIGIBILITY", "Eligibility"),
                            ("SUBMITTED", "Submitted"),
                            ("COMPLETE", "Complete"),
                        ],
                        max_length=64,
                    ),
                ),
                ("field_name", models.CharField(max_length=255)),
                ("image_id", models.CharField(blank=True, max_length=128, null=True)),
                (
                    "payload",
                    models.JSONField(blank=True, default=onboarding_v2.models.default_json),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("RESOLVED", "Resolved")],
                        default="PENDING",
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="corrections",
                        to="onboarding_v2.applicationv2",
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="applicationdocument",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("PAN", "PAN"),
                    ("AADHAAR", "Aadhaar"),
                    ("LIVE_PHOTO", "Live Photo"),
                    ("VOTER_ID", "Voter ID"),
                    ("DRIVING_LICENSE", "Driving License"),
                    ("PASSPORT", "Passport"),
                    ("MANREGA_CARD", "Manrega Card"),
                    ("OTHER", "Other"),
                    ("CATTLE", "Cattle"),
                    ("FRESH_LOAN", "Fresh Loan"),
                    ("PLEDGE_CARD", "Pledge Card"),
                    ("CUSTOMER_VISIT", "Customer Visit"),
                ],
                default="OTHER",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="applicationstagesnapshot",
            name="stage",
            field=models.CharField(
                choices=[
                    ("PAN", "Pan"),
                    ("BASIC", "Basic"),
                    ("ADDRESS", "Address"),
                    ("DOCUMENTS", "Documents"),
                    ("PERSONAL", "Personal"),
                    ("ADDRESS_SECONDARY", "AddressSecondary"),
                    ("GOLD", "Gold"),
                    ("PLEDGE_CARD", "Pledge Card"),
                    ("LOAN", "Loan"),
                    ("BANK", "Bank"),
                    ("ADDITIONAL", "Additional"),
                    ("CUSTOMER_VISIT", "Customer Visit"),
                    ("WAIVER", "Waiver"),
                    ("ELIGIBILITY", "Eligibility"),
                    ("SUBMITTED", "Submitted"),
                    ("COMPLETE", "Complete"),
                ],
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="applicationv2",
            name="stage",
            field=models.CharField(
                choices=[
                    ("PAN", "Pan"),
                    ("BASIC", "Basic"),
                    ("ADDRESS", "Address"),
                    ("DOCUMENTS", "Documents"),
                    ("PERSONAL", "Personal"),
                    ("ADDRESS_SECONDARY", "AddressSecondary"),
                    ("GOLD", "Gold"),
                    ("PLEDGE_CARD", "Pledge Card"),
                    ("LOAN", "Loan"),
                    ("BANK", "Bank"),
                    ("ADDITIONAL", "Additional"),
                    ("CUSTOMER_VISIT", "Customer Visit"),
                    ("WAIVER", "Waiver"),
                    ("ELIGIBILITY", "Eligibility"),
                    ("SUBMITTED", "Submitted"),
                    ("COMPLETE", "Complete"),
                ],
                default="PAN",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="applicationv2",
            name="status",
            field=models.CharField(
                choices=[
                    ("DRAFT", "Draft"),
                    ("SENT_FOR_PRE_SCREENING", "SentForPreScreening"),
                    ("IN_PROGRESS", "InProgress"),
                    ("READY_FOR_LOAN", "ReadyForLoan"),
                    ("APPROVED", "Approved"),
                    ("AGREEMENT_SIGNED", "AgreementSigned"),
                    ("DISBURSEMENT_READY", "DisbursementReady"),
                    ("DISBURSED", "Disbursed"),
                    ("MATURED", "Matured"),
                    ("DROPPED", "Dropped"),
                    ("DISBURSEMENT_CANCELLED", "DisbursementCancelled"),
                    ("DROP_REQUESTED", "DropRequested"),
                    ("ALLOCATION_PENDING", "AllocationPending"),
                    ("COMMERCIAL_PROCESSING", "CommercialProcessing"),
                    ("DEVIATION_REQUESTED", "DeviationRequested"),
                    ("CORRECTION", "Correction"),
                    (
                        "CORRECTION_RAISED_BY_UNDERWRITING",
                        "Correction raised by underwriting",
                    ),
                    ("REJECTED", "Rejected"),
                    ("ELIGIBLE", "Eligible"),
                    ("NOT_ELIGIBLE", "NotEligible"),
                    ("PASSED", "Passed"),
                    ("SUBMITTED", "Submitted"),
                    ("FAILED_TO_SUBMIT", "FailedToSubmit"),
                    ("FAILED_TO_SUBMIT_PRESCREEN", "FailedToSubmitPrescreen"),
                    ("FAILED_TO_SUBMIT_CREATE_LOAN", "FailedToSubmitCreateLoan"),
                    ("NEW_LEAD", "NewLead"),
                    ("UNVERIFIED", "Unverified"),
                    ("PUNCHING_PENDING", "Punching Pending"),
                    ("LOAN_STATUS_UPDATED", "Loan Status Updated"),
                ],
                default="DRAFT",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="leadautoclosuresetting",
            name="product_subcategory",
            field=models.CharField(
                choices=[
                    ("GOLD_LOAN", "Gold Loan"),
                    ("HOME_LOAN", "Home Loan"),
                    ("PERSONAL_LOAN", "Personal Loan"),
                    ("BUSINESS_LOAN", "Business Loan"),
                    ("LOAN_AGAINST_PROPERTY", "Loan Against Property"),
                    ("MOTOR_LOAN", "Motor Loan"),
                    ("WORKING_CAPITAL", "Working Capital"),
                    ("OVERDRAFT_DOD", "Overdraft(DOD)"),
                    ("HEALTH_INSURANCE", "Health Insurance"),
                    ("MOTOR_INSURANCE", "Motor Insurance"),
                    ("CREDIT_CARDS", "Credit Cards"),
                ],
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="leadv2",
            name="product_subcategory",
            field=models.CharField(
                blank=True,
                choices=[
                    ("GOLD_LOAN", "Gold Loan"),
                    ("HOME_LOAN", "Home Loan"),
                    ("PERSONAL_LOAN", "Personal Loan"),
                    ("BUSINESS_LOAN", "Business Loan"),
                    ("LOAN_AGAINST_PROPERTY", "Loan Against Property"),
                    ("MOTOR_LOAN", "Motor Loan"),
                    ("WORKING_CAPITAL", "Working Capital"),
                    ("OVERDRAFT_DOD", "Overdraft(DOD)"),
                    ("HEALTH_INSURANCE", "Health Insurance"),
                    ("MOTOR_INSURANCE", "Motor Insurance"),
                    ("CREDIT_CARDS", "Credit Cards"),
                ],
                max_length=64,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="leadv2",
            name="source",
            field=models.CharField(
                choices=[
                    ("SELF", "Self"),
                    ("BANK_REFERRED", "Bank Reffered"),
                    ("CENTRAL", "Central"),
                    ("TELE", "Tele"),
                    ("AGENT", "Agent"),
                    ("WEBSITE", "Website"),
                    ("DIGITAL_MARKETING", "Digital Marketing"),
                    ("BTL", "BTL"),
                    ("CSR", "CSR"),
                    ("WALK_IN", "Walk-in"),
                    ("REPEAT", "Repeat"),
                    ("DATABASE", "Database"),
                ],
                default="SELF",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="lendingpartnermaster",
            name="available_for",
            field=models.CharField(
                choices=[
                    ("GOLD_LOAN", "Gold Loan"),
                    ("HOME_LOAN", "Home Loan"),
                    ("PERSONAL_LOAN", "Personal Loan"),
                    ("BUSINESS_LOAN", "Business Loan"),
                    ("LOAN_AGAINST_PROPERTY", "Loan Against Property"),
                    ("MOTOR_LOAN", "Motor Loan"),
                    ("WORKING_CAPITAL", "Working Capital"),
                    ("OVERDRAFT_DOD", "Overdraft(DOD)"),
                    ("HEALTH_INSURANCE", "Health Insurance"),
                    ("MOTOR_INSURANCE", "Motor Insurance"),
                    ("CREDIT_CARDS", "Credit Cards"),
                ],
                max_length=64,
            ),
        ),
    ]
