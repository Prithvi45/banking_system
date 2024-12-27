# Generated by Django 5.1.4 on 2024-12-27 09:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_tenant'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankaccount',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.tenant'),
        ),
    ]