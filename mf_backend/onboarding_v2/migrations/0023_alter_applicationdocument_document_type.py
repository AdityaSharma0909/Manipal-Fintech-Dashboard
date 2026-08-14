from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding_v2", "0022_alter_leadv2_product_subcategory_and_source"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applicationdocument",
            name="document_type",
            field=models.CharField(
                choices=[
                    ("PAN", "PAN"),
                    ("AADHAAR", "Aadhaar"),
                    ("LIVE_PHOTO", "Live Photo"),
                    ("VOTER_ID", "Voter ID"),
                    ("DRIVING_LICENSE", "Driving License"),
                    ("PASSPORT", "Passport"),
                    ("OTHER", "Other"),
                ],
                default="OTHER",
                max_length=64,
            ),
        ),
    ]
