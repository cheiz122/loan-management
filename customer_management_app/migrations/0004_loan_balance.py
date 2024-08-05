# Generated by Django 5.0.7 on 2024-07-17 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_management_app', '0003_alter_loan_interest_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=1, editable=False, max_digits=10),
            preserve_default=False,
        ),
    ]
