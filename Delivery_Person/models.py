#Delivery_Person/models.py
from django.db import models
from RestauranteData.models import Restaurante
from Authentication.models import BaseUser

# Create your models here.
class Delivery_Person(models.Model):
    user = models.OneToOneField(BaseUser,on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.user.username