from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('onboarding_v2', '0052_merge_20260512_1256'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThirdPartyLender',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=255)),
                ('ifsc_code', models.CharField(max_length=11, validators=[django.core.validators.RegexValidator(message='Enter a valid IFSC code (e.g., SBIN0001234)', regex='^[A-Z]{4}0[A-Z0-9]{6}$')])),
                ('branch', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Third Party Lender',
                'verbose_name_plural': 'Third Party Lenders',
                'unique_together': {('bank_name', 'ifsc_code')},
            },
        ),
    ]
