from django.db import models
from RestauranteData.models import FoodItem
from Customer.models import Customer
from Order_Dispatcher.models import Order_Dispatcher
from Order_Manager.models import Order_Manager
from Delivery_Person.models import Delivery_Person
# Create your models here.
class Pedido (models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    customer=models.ForeignKey(Customer,null=True,on_delete=models.SET_NULL,blank=True)
    order_manager=models.ForeignKey(Order_Manager,null=True,on_delete=models.SET_NULL,blank=True)
    order_dispatcher=models.ForeignKey(Order_Dispatcher,null=True,on_delete=models.SET_NULL,blank=True)
    delivery_person=models.ForeignKey(Delivery_Person,null=True,on_delete=models.SET_NULL,blank=True)
    food_items = models.ManyToManyField(FoodItem, through='PedidoFoodItem')

    def __str__(self):
        return f"Pedido {self.id} - {self.description}"



class PedidoFoodItem(models.Model):
    pedido = models.ForeignKey(Pedido , on_delete=models.CASCADE)
    food_item = models.ForeignKey (FoodItem , on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.food_item.name} - {self.quantity}"