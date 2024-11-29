# Customer/serializers.py
from rest_framework import serializers
from .models import CartItem
from RestauranteData.models import FoodItem

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['food_item', 'quantity']
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")
        return value
