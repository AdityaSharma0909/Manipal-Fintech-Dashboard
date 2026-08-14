from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0031_user_remember_password_user_remember_username_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="timestamp",
            name="selfie",
            field=models.ImageField(
                blank=True, max_length=500, null=True, upload_to="media/selfie"
            ),
        ),
    ]
