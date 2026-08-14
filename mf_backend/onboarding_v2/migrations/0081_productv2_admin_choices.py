from django.db import migrations, models


def normalize_product_dropdown_values(apps, schema_editor):
    ProductV2 = apps.get_model("onboarding_v2", "ProductV2")
    category_map = {
        "Consumption Loan": "CONSUMPTION_LOAN",
        "Income Loan": "INCOME_LOAN",
    }
    repayment_map = {
        "Bullet": "BULLET",
        "Quarterly": "QUARTERLY",
        "Monthly": "MONTHLY",
    }
    available_for_map = {
        "Co-Lending": "CO_LENDING",
        "Co Lending": "CO_LENDING",
        "Self-Lending": "SELF_LENDING",
        "Self Lending": "SELF_LENDING",
    }

    for product in ProductV2.objects.all().iterator():
        update_fields = []
        normalized_category = category_map.get(product.category, product.category)
        if normalized_category != product.category:
            product.category = normalized_category
            update_fields.append("category")

        normalized_repayment = repayment_map.get(
            product.repayment_frequency,
            product.repayment_frequency,
        )
        if normalized_repayment != product.repayment_frequency:
            product.repayment_frequency = normalized_repayment
            update_fields.append("repayment_frequency")

        normalized_available_for = [
            available_for_map.get(value, value)
            for value in (product.available_for or [])
        ]
        if normalized_available_for != (product.available_for or []):
            product.available_for = normalized_available_for
            update_fields.append("available_for")

        if update_fields:
            product.save(update_fields=update_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0080_productv2"),
    ]

    operations = [
        migrations.RunPython(
            normalize_product_dropdown_values,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="productv2",
            name="category",
            field=models.CharField(
                choices=[
                    ("CONSUMPTION_LOAN", "Consumption Loan"),
                    ("INCOME_LOAN", "Income Loan"),
                ],
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name="productv2",
            name="repayment_frequency",
            field=models.CharField(
                choices=[
                    ("BULLET", "Bullet"),
                    ("QUARTERLY", "Quarterly"),
                    ("MONTHLY", "Monthly"),
                ],
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="productv2",
            name="tenure_months",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (3, "3 months"),
                    (4, "4 months"),
                    (6, "6 months"),
                    (9, "9 months"),
                    (12, "12 months"),
                ],
            ),
        ),
    ]
