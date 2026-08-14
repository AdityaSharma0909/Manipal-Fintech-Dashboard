from django.db import migrations, models
import uuid
from onboarding_v2.models import default_json


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0005_alter_additionaldetailsv2_metadata_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebhookEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("application_id", models.CharField(max_length=128)),
                ("request_id", models.CharField(blank=True, max_length=128, null=True)),
                ("payload", models.JSONField(blank=True, default=default_json)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("RECEIVED", "Received"),
                            ("QUEUED", "Queued"),
                            ("PROCESSED", "Processed"),
                            ("FAILED", "Failed"),
                        ],
                        default="RECEIVED",
                        max_length=16,
                    ),
                ),
                ("last_error", models.TextField(blank=True, null=True)),
                ("retry_count", models.IntegerField(default=0)),
                ("next_retry_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddIndex(
            model_name="webhookevent",
            index=models.Index(fields=["application_id"], name="onboarding__applic_3f8334_idx"),
        ),
        migrations.AddIndex(
            model_name="webhookevent",
            index=models.Index(fields=["request_id"], name="onboarding__request_c9b60e_idx"),
        ),
        migrations.AddIndex(
            model_name="webhookevent",
            index=models.Index(fields=["status", "next_retry_at"], name="onboarding__status__n_3c6f7f_idx"),
        ),
    ]

