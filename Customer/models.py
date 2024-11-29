#Customer/models.py
from django.db import models
from RestauranteData.models import Restaurante
from Authentication.models import BaseUser
from RestauranteData.models import FoodItem

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(BaseUser,on_delete=models.CASCADE)
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE)
    phone = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.username
    
class Cart (models.Model):
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)

class CartItem (models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)