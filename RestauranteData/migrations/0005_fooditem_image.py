# Generated by Django 5.1.3 on 2024-11-29 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('RestauranteData', '0004_fooditem_stockrestaurant'),
    ]

    operations = [
        migrations.AddField(
            model_name='fooditem',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='food_items/'),
        ),
    ]
