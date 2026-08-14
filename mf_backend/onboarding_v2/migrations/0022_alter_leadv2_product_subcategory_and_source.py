from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding_v2", "0021_add_lead_type"),
    ]

    operations = [
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
                    ("HEALTH_INSURANCE", "Health Insurance"),
                    ("MOTOR_INSURANCE", "Motor Insurance"),
                ],
                max_length=64,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="leadv2",
            name="source",
            field=models.CharField(
                choices=[("SELF", "Self"), ("BANK_REFERRED", "Bank Reffered"), ("CENTRAL", "Central")],
                default="SELF",
                max_length=32,
            ),
        ),
    ]
