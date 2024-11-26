from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import BaseUser
from Administrator.models import Administrator
from Customer.models import Customer
from RestauranteData.models import Restaurante
from django.db import transaction
from Delivery_Person.models import Delivery_Person
from Menu_Manager.models import Menu_Manager
from Order_Dispatcher.models import Order_Dispatcher
from Order_Manager.models import Order_Manager

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
            elif validated_data['role'] == 'delivery_person':
                Delivery_Person.objects.create(user=user)
            elif validated_data['role'] == 'menu_manager':
                Menu_Manager.objects.create(user=user,restaurante=restaurant)
            elif validated_data['role'] == 'order_dispatcher':
                Order_Dispatcher.objects.create(user=user,restaurante=restaurant)
            elif validated_data['role'] == 'order_manager':
                Order_Manager.objects.create(user=user,restaurante=restaurant)

        return user

class UserTokenSerializer(serializers.ModelSerializer):
    acces_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    class Meta:
        model = BaseUser
        fields = ['username', 'acces_token', 'refresh_token']
