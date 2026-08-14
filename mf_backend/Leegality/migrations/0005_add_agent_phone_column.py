# 0001_initial already creates LeegalityDocument with agent_phone; no-op to avoid DuplicateColumn.
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Leegality', '0004_add_agent_phone'),
    ]

    operations = []
