from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0081_productv2_admin_choices"),
    ]

    operations = [
        migrations.AddField(
            model_name="lendingpartnermaster",
            name="available_for_lead_type",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Lead types for which the lending partner is available",
            ),
        ),
    ]
