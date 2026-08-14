from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0027_alter_subtask_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtask',
            name='decline_reason',
            field=models.TextField(null=True, blank=True),
        ),
    ]

