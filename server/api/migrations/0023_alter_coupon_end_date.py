# Generated by Django 5.1.7 on 2025-04-12 21:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_alter_coupon_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 5, 12, 21, 56, 5, 607952, tzinfo=datetime.timezone.utc)),
        ),
    ]
