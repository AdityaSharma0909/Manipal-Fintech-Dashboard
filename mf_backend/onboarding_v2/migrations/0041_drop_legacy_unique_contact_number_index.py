from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("onboarding_v2", "0040_alter_bankbranch_unique_together_and_more"),
    ]

    operations = [
        # Legacy DBs may still retain a unique constraint/index on contact_number.
        # Remove it to align with model state (db_index=True, not unique).
        migrations.RunSQL(
            sql=(
                "ALTER TABLE onboarding_v2_leadv2 "
                "DROP CONSTRAINT IF EXISTS onboarding_v2_leadv2_contact_number_5b9b44ab_uniq; "
                "DROP INDEX IF EXISTS onboarding_v2_leadv2_contact_number_5b9b44ab_uniq; "
                "DROP INDEX IF EXISTS onboarding_v2_leadv2_contact_number_5b9b44ab; "
                "CREATE INDEX IF NOT EXISTS onboarding_v2_leadv2_contact_number_5b9b44ab "
                "ON onboarding_v2_leadv2 (contact_number);"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
