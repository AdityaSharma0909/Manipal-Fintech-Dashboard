from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0037_loanpunchv2_agent_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="LendingPartnerMaster",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("bank_name", models.CharField(max_length=255)),
                (
                    "available_for",
                    models.CharField(
                        choices=[
                            ("GOLD_LOAN", "Gold Loan"),
                            ("HOME_LOAN", "Home Loan"),
                            ("PERSONAL_LOAN", "Personal Loan"),
                            ("BUSINESS_LOAN", "Business Loan"),
                            ("LOAN_AGAINST_PROPERTY", "Loan Against Property"),
                            ("MOTOR_LOAN", "Motor Loan"),
                            ("HEALTH_INSURANCE", "Health Insurance"),
                            ("MOTOR_INSURANCE", "Motor Insurance"),
                        ],
                        max_length=64,
                    ),
                ),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "unique_together": {("bank_name", "available_for")},
            },
        ),
    ]
