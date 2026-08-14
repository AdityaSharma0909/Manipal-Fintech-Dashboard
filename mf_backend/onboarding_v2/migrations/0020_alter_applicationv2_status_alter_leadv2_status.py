from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding_v2", "0019_add_saas_prescreen_raw"),
    ]

    operations = [
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
                    ("REJECTED", "Rejected"),
                    ("ELIGIBLE", "Eligible"),
                    ("NOT_ELIGIBLE", "NotEligible"),
                    ("PASSED", "Passed"),
                    ("SUBMITTED", "Submitted"),
                    ("FAILED_TO_SUBMIT", "FailedToSubmit"),
                    ("FAILED_TO_SUBMIT_PRESCREEN", "FailedToSubmitPrescreen"),
                    ("FAILED_TO_SUBMIT_CREATE_LOAN", "FailedToSubmitCreateLoan"),
                ],
                default="DRAFT",
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="leadv2",
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
                    ("REJECTED", "Rejected"),
                    ("ELIGIBLE", "Eligible"),
                    ("NOT_ELIGIBLE", "NotEligible"),
                    ("PASSED", "Passed"),
                    ("SUBMITTED", "Submitted"),
                    ("FAILED_TO_SUBMIT", "FailedToSubmit"),
                    ("FAILED_TO_SUBMIT_PRESCREEN", "FailedToSubmitPrescreen"),
                    ("FAILED_TO_SUBMIT_CREATE_LOAN", "FailedToSubmitCreateLoan"),
                ],
                default="DRAFT",
                max_length=64,
            ),
        ),
    ]
