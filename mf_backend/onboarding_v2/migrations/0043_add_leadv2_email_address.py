from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0042_alter_applicationv2_loan_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="leadv2",
            name="email_address",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]