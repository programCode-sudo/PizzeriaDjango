# Order_Manager/serializers.py
from rest_framework import serializers
from Delivery_Person.models import Delivery_Person
from Authentication.models import BaseUser

class DeliveryPersonSerializer(serializers.ModelSerializer):
    # Obtener el nombre completo del repartidor
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    role = serializers.CharField(source='user.role')

    class Meta:
        model = Delivery_Person
        fields = ['id','first_name', 'last_name', 'email', 'role']