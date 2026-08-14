from django.db import migrations, models


def rename_bt_to_balance_transfer(apps, schema_editor):
    LeadV2 = apps.get_model("onboarding_v2", "LeadV2")
    ApplicationV2 = apps.get_model("onboarding_v2", "ApplicationV2")
    LeadAutoClosureSetting = apps.get_model("onboarding_v2", "LeadAutoClosureSetting")

    LeadV2.objects.filter(lead_type="BT").update(lead_type="BALANCE_TRANSFER")
    ApplicationV2.objects.filter(loan_type="BT").update(loan_type="BALANCE_TRANSFER")
    LeadAutoClosureSetting.objects.filter(lead_type="BT").update(lead_type="BALANCE_TRANSFER")


def rename_balance_transfer_to_bt(apps, schema_editor):
    LeadV2 = apps.get_model("onboarding_v2", "LeadV2")
    ApplicationV2 = apps.get_model("onboarding_v2", "ApplicationV2")
    LeadAutoClosureSetting = apps.get_model("onboarding_v2", "LeadAutoClosureSetting")

    LeadV2.objects.filter(lead_type="BALANCE_TRANSFER").update(lead_type="BT")
    ApplicationV2.objects.filter(loan_type="BALANCE_TRANSFER").update(loan_type="BT")
    LeadAutoClosureSetting.objects.filter(lead_type="BALANCE_TRANSFER").update(lead_type="BT")


LEAD_TYPE_CHOICES = [
    ("FRESH", "Fresh"),
    ("BALANCE_TRANSFER", "Balance Transfer"),
    ("CO_LENDING", "Co-Lending"),
]


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0040_alter_bankbranch_unique_together_and_more"),
    ]

    operations = [
        migrations.RunPython(
            rename_bt_to_balance_transfer,
            reverse_code=rename_balance_transfer_to_bt,
        ),
        migrations.AlterField(
            model_name="leadv2",
            name="lead_type",
            field=models.CharField(
                blank=True,
                choices=LEAD_TYPE_CHOICES,
                max_length=32,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="applicationv2",
            name="loan_type",
            field=models.CharField(
                blank=True,
                choices=LEAD_TYPE_CHOICES,
                max_length=32,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="leadautoclosuresetting",
            name="lead_type",
            field=models.CharField(
                choices=LEAD_TYPE_CHOICES,
                max_length=32,
            ),
        ),
    ]
