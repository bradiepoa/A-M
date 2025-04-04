# Generated by Django 5.1.7 on 2025-03-30 12:59

import datetime
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_coupon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 4, 29, 12, 59, 57, 306710, tzinfo=datetime.timezone.utc)),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('payment_id', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.TextField()),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shipping', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('service_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('initial_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('saves', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('payment_method', models.CharField(choices=[('credit_card', 'Credit Card'), ('paypal', 'PayPal'), ('bank_transfer', 'Bank Transfer'), ('cod', 'Cash on Delivery')], default='credit_card', max_length=20)),
                ('order_status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('canceled', 'Canceled')], default='pending', max_length=20)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.coupon')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_orders', to='api.user')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_orders', to='api.user')),
            ],
        ),
    ]
