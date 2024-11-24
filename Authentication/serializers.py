from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import BaseUser
from Administrator.models import Administrator
from Customer.models import Customer
from RestauranteData.models import Restaurante
from django.db import transaction

class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=BaseUser.ROLE_CHOICES)

    class Meta:
        model = BaseUser
        fields = ['username', 'password', 'email', 'role']

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = BaseUser(**validated_data)
        user.set_password(password)

        # Crear al usuario y asignar el restaurante
        with transaction.atomic():
            user.save()
            restaurant, _ = Restaurante.objects.get_or_create(
                name="Pizza Lovers",
                defaults={
                    "description": "Somos una pizzería independiente de buena calidad vendemos las mejores pizzas en San Salvador",
                    "lealtad_points": False,
                }
            )

            # Asociar el restaurante según el rol
            if validated_data['role'] == 'customer':
                Customer.objects.create(user=user, restaurante=restaurant)
            elif validated_data['role'] == 'administrator':
                Administrator.objects.create(user=user, restaurante=restaurant)

        return user

class UserTokenSerializer(serializers.ModelSerializer):
    acces_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta:
        model = BaseUser
        fields = ['username', 'acces_token', 'refresh_token']
