from django.urls import path
from .views import ActualizarEstadoPedidoDispatcherAPIView

urlpatterns = [
    path('updateStatus/<int:pedido_id>/',ActualizarEstadoPedidoDispatcherAPIView.as_view(),name='updatestatus')
]
