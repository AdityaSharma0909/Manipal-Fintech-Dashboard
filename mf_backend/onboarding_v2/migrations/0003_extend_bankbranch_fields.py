from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding_v2', '0002_pincodemaster'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankbranch',
            name='agent_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='bankbranch',
            name='agent_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bankbranch',
            name='agent_wise_status',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bankbranch',
            name='correct_district',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bankbranch',
            name='district',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bankbranch',
            name='glo_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='bankbranch',
            name='glo_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='bankbranch',
            name='sol_id',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
