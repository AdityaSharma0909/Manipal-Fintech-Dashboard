from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding_v2", "0018_alter_applicationv2_status_alter_leadv2_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicationv2",
            name="saas_prescreen_raw",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
