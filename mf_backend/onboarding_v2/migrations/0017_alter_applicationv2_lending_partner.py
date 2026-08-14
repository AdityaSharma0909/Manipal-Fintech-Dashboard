from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0016_remove_bankdetailsv2_cheque_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applicationv2",
            name="lending_partner",
            field=models.CharField(
                blank=True,
                choices=[("AXIS_BANK", "Axis Bank")],
                default="AXIS_BANK",
                max_length=64,
                null=True,
            ),
        ),
    ]
