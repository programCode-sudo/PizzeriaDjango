#RestauranteData/Food_Item.py
from django.db import models
#modelo de los items de comida del resturante (menu)
class FoodItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    unitPrice = models.FloatField()
    stockRestaurant = models.IntegerField(default=0);
    image = models.ImageField(upload_to='food_items/',null=True,blank=True)

    def _str_(self):
        return self.name