#RestauranteAPI/urls.py

"""
URL configuration for RestauranteAPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('Authentication.urls')),
    path('administrator/',include('Administrator.urls')),
    path('menu_manager/',include('Menu_Manager.urls')),
    path('customer/',include('Customer.urls')),
    path('api/token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
    path('pedidos/',include('Pedidos.urls')),
    path('order_manager/',include('Order_Manager.urls')),
    path('delivery_person/',include('Delivery_Person.urls')),
    path('order_dispatcher/',include('Order_Dispatcher.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
