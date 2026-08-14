from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0078_alter_applicationstatushistory_to_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="loanpunchv2",
            name="loan_account_document",
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name="loanpunchv2",
            name="product_approval_screenshot",
            field=models.URLField(blank=True, max_length=2048, null=True),
        ),
    ]
