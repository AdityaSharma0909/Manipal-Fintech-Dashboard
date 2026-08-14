from django.db import migrations


class Migration(migrations.Migration):
    """
    Merge migration to resolve conflicting 0012 migrations:
    - 0012_alter_idsequence_id_alter_leadv2_product_subcategory
    - 0012_webhook_purpose_and_remarks
    """

    dependencies = [
        ("onboarding_v2", "0012_alter_idsequence_id_alter_leadv2_product_subcategory"),
        ("onboarding_v2", "0012_webhook_purpose_and_remarks"),
    ]

    operations = []
