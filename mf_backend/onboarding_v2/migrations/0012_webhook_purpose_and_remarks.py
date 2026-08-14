from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding_v2", "0011_id_sequences_and_lead_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicationv2",
            name="saas_prescreen_remarks",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="saas_loan_remarks",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="webhookevent",
            name="purpose",
            field=models.CharField(
                choices=[
                    ("PRESCREEN", "Pre-screen"),
                    ("LOAN_CREATION", "Loan Creation"),
                    ("UNKNOWN", "Unknown"),
                ],
                default="UNKNOWN",
                max_length=32,
            ),
        ),
    ]
