# Generated by Django 5.1.3 on 2024-11-28 01:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0002_alter_baseuser_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='email',
            field=models.EmailField(error_messages={'unique:Este email ya esta registrado'}, max_length=254, unique=True, validators=[django.core.validators.EmailValidator()]),
        ),
    ]
