from django.db import migrations, models
import onboarding_v2.models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding_v2', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PincodeMaster',
            fields=[
                ('pincode', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('district', models.CharField(blank=True, max_length=255, null=True)),
                ('statename', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.CharField(blank=True, max_length=64, null=True)),
                ('longitude', models.CharField(blank=True, max_length=64, null=True)),
                ('circlename', models.CharField(blank=True, max_length=255, null=True)),
                ('regionname', models.CharField(blank=True, max_length=255, null=True)),
                ('divisionname', models.CharField(blank=True, max_length=255, null=True)),
                ('metadata', models.JSONField(blank=True, default=onboarding_v2.models.default_json)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
