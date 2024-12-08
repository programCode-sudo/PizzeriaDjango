from django.urls import path
from .views import ActualizarEstadoDeliveryPersonAPIView,VerPedidosPorRepartidorAPIView,CambiarEstadoPedidoAPIView,BorrarPedidoAPIView

urlpatterns = [
    path('changeIsOnline/',ActualizarEstadoDeliveryPersonAPIView.as_view(),name='changeonline'),
    path('viewOrders/',VerPedidosPorRepartidorAPIView.as_view(),name='vierorders'),
    path('changeOrderStatus/<int:pedido_id>/',CambiarEstadoPedidoAPIView.as_view(),name='changeorderstatus'),
    path('deleteOrder/<int:pedido_id>',BorrarPedidoAPIView.as_view(),name='deletepedido')
]
