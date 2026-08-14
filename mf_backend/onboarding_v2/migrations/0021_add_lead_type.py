from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding_v2", "0020_alter_applicationv2_status_alter_leadv2_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="leadv2",
            name="lead_type",
            field=models.CharField(blank=True, choices=[("FRESH", "Fresh"), ("BT", "BT"), ("CO_LENDING", "Co-Lending")], max_length=32, null=True),
        ),
    ]
