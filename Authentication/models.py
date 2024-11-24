# Authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class BaseUser(AbstractUser):
    ROLE_CHOICES = [
        ('administrator', 'Administrator'),
        ('customer', 'Customer'),
        ('menu_manager', 'Menu Manager'),
        ('delivery_person', 'Delivery Person'),
        ('order_manager', 'Order Manager'),
        ('order_dispatcher', 'Order Dispatcher')
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer',
    )

    def __str__(self):
        return f"{self.username} ({self.role})"