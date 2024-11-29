# Generated by Django 5.1.3 on 2024-11-29 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pedidos', '0002_pedido_customer_pedido_delivery_person_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='food_items',
        ),
        migrations.RemoveField(
            model_name='pedidofooditem',
            name='food_item',
        ),
        migrations.AddField(
            model_name='pedidofooditem',
            name='food_item_image',
            field=models.ImageField(blank=True, null=True, upload_to='Pedidos_Img_items/'),
        ),
        migrations.AddField(
            model_name='pedidofooditem',
            name='food_item_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='pedidofooditem',
            name='food_item_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='pedidofooditem',
            name='quantity',
            field=models.IntegerField(default=0),
        ),
    ]
