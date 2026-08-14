import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0070_customers"),
    ]

    operations = [
        migrations.CreateModel(
            name="Banner",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "file_url",
                    models.URLField(
                        max_length=2048,
                        help_text="Publicly accessible URL of the banner image",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=255, help_text="Banner title"),
                ),
                (
                    "message",
                    models.TextField(help_text="Banner message body"),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True,
                        default=True,
                        help_text="Whether the banner is currently active",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Banner",
                "verbose_name_plural": "Banners",
                "db_table": "Banner",
                "ordering": ["-created_at"],
            },
        ),
    ]
