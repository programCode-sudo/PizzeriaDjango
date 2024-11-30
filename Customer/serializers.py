# Customer/serializers.py
from rest_framework import serializers
from .models import CartItem,LoyaltyPoint,Coupon,Customer
from RestauranteData.models import FoodItem

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['food_item', 'quantity']
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")
        return value

class LoyaltyPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyPoint
        fields = ['points', 'created_at']

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['discount_amount', 'created_at', 'expires_at']

class CustomerProfileSerializer(serializers.ModelSerializer):
    loyalty_points = LoyaltyPointSerializer(many=True)
    coupons = CouponSerializer(many=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    phone = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ['id', 'customer_addres', 'comprasRealizadas', 'loyalty_points', 'coupons', 'first_name', 'last_name', 'email', 'phone']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['customer_id'] = instance.id
        return data
