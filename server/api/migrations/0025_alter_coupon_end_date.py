# Generated by Django 5.1.7 on 2025-04-13 12:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_alter_coupon_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 5, 13, 12, 26, 8, 377953, tzinfo=datetime.timezone.utc)),
        ),
    ]
