# Authentication/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import BaseUser
from Administrator.models import Administrator
from Customer.models import Customer,Cart
from RestauranteData.models import Restaurante
from django.db import transaction
from Delivery_Person.models import Delivery_Person
from Menu_Manager.models import Menu_Manager
from Order_Dispatcher.models import Order_Dispatcher
from Order_Manager.models import Order_Manager


class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=BaseUser.ROLE_CHOICES)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = BaseUser
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'role']

    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if BaseUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        if BaseUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

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
                customer = Customer.objects.create(user=user, restaurante=restaurant)
                # Crear el carrito para el cliente
                Cart.objects.create(customer=customer)
            elif validated_data['role'] == 'administrator':
                Administrator.objects.create(user=user, restaurante=restaurant)
            elif validated_data['role'] == 'delivery_person':
                Delivery_Person.objects.create(user=user)
            elif validated_data['role'] == 'menu_manager':
                Menu_Manager.objects.create(user=user, restaurante=restaurant)
            elif validated_data['role'] == 'order_dispatcher':
                Order_Dispatcher.objects.create(user=user, restaurante=restaurant)
            elif validated_data['role'] == 'order_manager':
                Order_Manager.objects.create(user=user, restaurante=restaurant)

        return user


class EditUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)  # Contraseña opcional

    class Meta:
        model = BaseUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password']

    def validate_email(self, value):
        user_id = self.instance.id  # ID del usuario que se está editando
        if BaseUser.objects.filter(email=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        user_id = self.instance.id
        if BaseUser.objects.filter(username=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def update(self, instance, validated_data):
        # Si se proporciona contraseña, actualizarla con hashing
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # Actualizar otros campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance