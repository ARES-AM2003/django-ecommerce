# Generated by Django 5.1.7 on 2025-04-05 20:19

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_id',
            field=models.CharField(blank=True, default=uuid.uuid4, max_length=100, null=True, unique=True),
        ),
    ]
