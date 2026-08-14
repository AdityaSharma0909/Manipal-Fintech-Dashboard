from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicationv2",
            name="agreement_id",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="applicant_profession",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="bureau_name",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="bureau_pull_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="bureau_reference_number",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="bureau_report_link",
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="caste",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="compliance",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="consent_ip",
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="consent_timestamp",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="documentation_charges",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="first_repayment_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="insurance_charges",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="interest_start_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="income_source",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="loan_maturity_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="ltr",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="multi_appraisal",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="nationality",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="nri_status",
            field=models.CharField(
                blank=True,
                choices=[("Y", "Yes"), ("N", "No")],
                max_length=1,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="occupation",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="other_charges",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="partner_branch_code",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="partner_branch_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="partner_product_code",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="primary_borrower_type",
            field=models.CharField(
                blank=True,
                choices=[("INDIVIDUAL", "Individual"), ("CORPORATE", "Corporate")],
                max_length=32,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="processing_fee",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="reference_number",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="source_id",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="spread_id",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="stamp_duty",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
        migrations.AddField(
            model_name="applicationv2",
            name="total_charges",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True),
        ),
    ]
