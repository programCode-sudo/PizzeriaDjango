from django.urls import path
from .views import RegisterView,LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # Ruta para el registro
    path('login/', LoginView.as_view(),name='login'), #Ruta para login
]
