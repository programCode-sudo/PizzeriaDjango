# Generated by Django 5.1.3 on 2024-11-29 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pedidos', '0003_remove_pedido_food_items_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='Total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]