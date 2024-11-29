#Customer/models.py
from django.db import models
from RestauranteData.models import Restaurante
from Authentication.models import BaseUser
from RestauranteData.models import FoodItem
from datetime import timedelta
from django.utils.timezone import now
from django.utils import timezone
# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(BaseUser,on_delete=models.CASCADE)
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    phone = models.IntegerField(default=0)
    comprasRealizadas = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.username
    
class Cart (models.Model):
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

class CartItem (models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

class LoyaltyPoint(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loyalty_points')
    points = models.IntegerField(default=0)  # Puntos acumulados
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return now() > self.created_at + timedelta(days=60)  # Expira a los 2 meses

def default_expiration_date():
    """Calcula la fecha de expiración por defecto para los cupones."""
    return now() + timedelta(days=5)
class Coupon(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='coupons')
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, default=10.00)  # Valor del cupón
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiration_date)

    def is_expired(self):
        return now() > self.expires_at

    def __str__(self):
        return f"Cupón: ${self.discount_amount} para {self.customer.user.username}"