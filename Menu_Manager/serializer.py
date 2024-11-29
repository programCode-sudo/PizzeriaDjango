# Menu_Manager/serializers.py
from rest_framework import serializers
from RestauranteData.Food_Item import FoodItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['name', 'description', 'category', 'unitPrice', 'stockRestaurant', 'image']
