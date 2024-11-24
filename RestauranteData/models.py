from django.db import models
from .Food_Item import FoodItem
# Create your models here.
#modelo para el restaurante en general
class Restaurante(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    lealtad_points = models.BooleanField(default=False)

    food_item = models.ManyToManyField(FoodItem)
    def __str__(self):
        return self.name
