# Generated by Django 5.1.7 on 2025-05-03 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_user_auth_provider'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='auth_provider',
            field=models.CharField(default='email', max_length=50),
        ),
    ]
