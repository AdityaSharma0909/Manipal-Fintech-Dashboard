from django.db import migrations


def normalize_eligible_status(apps, schema_editor):
    ApplicationV2 = apps.get_model("onboarding_v2", "ApplicationV2")
    LeadV2 = apps.get_model("onboarding_v2", "LeadV2")

    ApplicationV2.objects.filter(status="ELIGIBLE").update(status="READY_FOR_LOAN")
    LeadV2.objects.filter(status="ELIGIBLE").update(status="READY_FOR_LOAN")


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding_v2", "0060_alter_applicationv2_status_bt_return_completed"),
    ]

    operations = [
        migrations.RunPython(normalize_eligible_status, migrations.RunPython.noop),
    ]
