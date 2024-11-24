from django.db import migrations


def create_default_restaurant(apps, schema_editor):
    Restaurante = apps.get_model('RestauranteData', 'Restaurante')
    Restaurante.objects.get_or_create(
        name="Pizza Lovers",
        description="Somos una pizzeria independiente de buena calidad vendemos las mejores pizzas San salvador",
        lealtad_points=False
    )


class Migration(migrations.Migration):
    dependencies = [
        ('RestauranteData', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_restaurant),
    ]
