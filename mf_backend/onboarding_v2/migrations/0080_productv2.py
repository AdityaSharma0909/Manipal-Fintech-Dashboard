import uuid

from django.db import migrations, models
import onboarding_v2.models


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0079_self_lending_flow"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductV2",
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
                    "available_for",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Lead types for which the product is available",
                    ),
                ),
                ("category", models.CharField(max_length=64)),
                (
                    "product_code",
                    models.CharField(
                        db_index=True,
                        max_length=32,
                        unique=True,
                    ),
                ),
                ("repayment_frequency", models.CharField(max_length=32)),
                ("tenure_months", models.PositiveSmallIntegerField()),
                (
                    "ltv",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="LTV percentage, e.g. 80.0000 means 80%",
                        max_digits=7,
                    ),
                ),
                (
                    "minimum_ticket_size",
                    models.DecimalField(decimal_places=2, max_digits=14),
                ),
                (
                    "maximum_ticket_size",
                    models.DecimalField(decimal_places=2, max_digits=14),
                ),
                (
                    "interest_rate",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="Annual interest percentage",
                        max_digits=7,
                    ),
                ),
                (
                    "processing_fees",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="Processing fee percentage",
                        max_digits=7,
                    ),
                ),
                (
                    "processing_fees_with_cbo_approval",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="Processing fee percentage with CBO approval",
                        max_digits=7,
                    ),
                ),
                (
                    "monthly_penalty_on_principal_outstanding",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="Monthly penalty percentage on outstanding principal",
                        max_digits=7,
                    ),
                ),
                (
                    "non_release_penalty",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="Penalty percentage when gold is not released within 7 days",
                        max_digits=7,
                    ),
                ),
                (
                    "foreclosure_charges",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="Foreclosure charge percentage within 30 days",
                        max_digits=7,
                    ),
                ),
                ("stamp_duty", models.CharField(max_length=255)),
                ("source_effective_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                (
                    "metadata",
                    models.JSONField(
                        blank=True,
                        default=onboarding_v2.models.default_json,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Product V2",
                "verbose_name_plural": "Products V2",
                "db_table": "ProductV2",
                "ordering": [
                    "category",
                    "repayment_frequency",
                    "tenure_months",
                    "product_code",
                ],
            },
        ),
    ]
