from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0023_alter_subtaskapproval_approval_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="subtasktracker",
            name="bank_name",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name="subtasktracker",
            name="customer_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="subtasktracker",
            name="lead_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("FRESH", "FRESH"),
                    ("TAKE_OVER_BT", "TAKE_OVER_BT"),
                    ("LOAN", "LOAN"),
                    ("INSURANCE", "INSURANCE"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="subtasktracker",
            name="loan_account_number",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="subtasktracker",
            name="loan_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
