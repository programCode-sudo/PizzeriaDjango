# Generated by Django 5.1.3 on 2024-11-29 10:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Customer', '0005_coupon_loyaltypoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 12, 4, 10, 31, 48, 847465, tzinfo=datetime.timezone.utc)),
        ),
    ]