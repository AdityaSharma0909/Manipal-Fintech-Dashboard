"""
migrations/0001_initial.py
==========================
Initial Django ORM migration creating:
  - bajaj_branch_detail
  - bajaj_lead_integration  (indexes on mobile_no + lead_status)
  - bajaj_lead_audit_logs   (FK to Lead)
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies: list = []

    operations = [
        # ── Branch ────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Branch",
            fields=[
                ("branch_id", models.IntegerField(primary_key=True, serialize=False)),
                ("branch_name", models.CharField(max_length=255)),
                ("branch_code", models.CharField(db_index=True, max_length=50)),
                ("pincode", models.CharField(max_length=10)),
                ("district_id", models.IntegerField(blank=True, db_index=True, null=True)),
            ],
            options={
                "verbose_name_plural": "Branches",
                "db_table": "bajaj_branch_detail",
            },
        ),
        # ── Lead ──────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Lead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=40)),
                ("last_name", models.CharField(blank=True, max_length=40, null=True)),
                ("mobile_no", models.CharField(db_index=True, max_length=15)),
                ("pincode", models.CharField(max_length=10)),
                ("loan_amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("created_by", models.BigIntegerField()),
                ("bank_id", models.BigIntegerField()),
                ("crm_id", models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ("api_message", models.TextField(blank=True, null=True)),
                ("state", models.CharField(max_length=100)),
                ("district", models.CharField(max_length=100)),
                ("branch", models.CharField(max_length=100)),
                (
                    "lead_status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Success", "Success"),
                            ("Failed", "Failed"),
                            ("Duplicate", "Duplicate"),
                            ("Rejected", "Rejected"),
                        ],
                        default="Failed",
                        max_length=20,
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "bajaj_lead_integration",
            },
        ),
        migrations.AddIndex(
            model_name="lead",
            index=models.Index(fields=["mobile_no", "lead_status"], name="bajaj_lead_mobile_status_idx"),
        ),
        # ── LeadAudit ─────────────────────────────────────────────────────────
        migrations.CreateModel(
            name="LeadAudit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "lead",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audits",
                        to="crm_integration.lead",
                    ),
                ),
                ("encrypted_request", models.TextField()),
                ("encrypted_response", models.TextField(blank=True, null=True)),
                ("plain_request", models.TextField()),
                ("plain_response", models.TextField(blank=True, null=True)),
                ("file_path", models.CharField(blank=True, max_length=500, null=True)),
                ("logged_in_user", models.BigIntegerField()),
                ("created_on", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "bajaj_lead_audit_logs",
            },
        ),
    ]
