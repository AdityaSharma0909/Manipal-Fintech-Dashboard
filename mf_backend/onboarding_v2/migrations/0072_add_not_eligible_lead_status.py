from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0071_applicationv2_client_loan_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="leadv2",
            name="status",
            field=models.CharField(
                choices=[
                    ("UNVERIFIED", "Unverified"),
                    ("ACTIVE", "Active"),
                    ("AUTO_CLOSED", "Auto-closed"),
                    ("APPLICATION_CREATED", "Application created"),
                    ("NOT_ELIGIBLE", "Not eligible"),
                ],
                default="ACTIVE",
                max_length=64,
            ),
        ),
    ]
