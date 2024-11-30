from django.urls import path
from .views import CreatePedidoAPIView,ListarPedidosAPIView,CancelarPedidoAPIView,VerPedidoDetalladoAPIView,BorrarPedidoAPIView,ListarPedidosPorEstadoAPIView
from .views import ListarRepartidoresAPIView,ListarRepartidoresPaginationAPIView,AsociarRepartidorAPedidoAPIView

urlpatterns = [
    path('createOrder/',CreatePedidoAPIView.as_view(),name='createorder'),
    path('viewAllOrders/',ListarPedidosAPIView.as_view(),name='viewAllOrders'),
    path('cancelOrder/<int:pedido_id>/',CancelarPedidoAPIView.as_view(),name='cancelorder'),
    path('deleteOrder/<int:pedido_id>/',BorrarPedidoAPIView.as_view(),name='deleteorder'),
    path('viewOrderDetail/<int:pedido_id>/',VerPedidoDetalladoAPIView.as_view(),name='vieworderdetail'),
    path('viewOrdersForStatus/',ListarPedidosPorEstadoAPIView.as_view(),name='viewordersforstatus'),
    path('viewAllDeliverysForStatus/',ListarRepartidoresAPIView.as_view(),name='viewAllDeliverys'),
    path('viewAllDeliverysPagination/',ListarRepartidoresPaginationAPIView.as_view(),name='viewDeliverypagination'),
    path('linkDeliveryToOrder/',AsociarRepartidorAPedidoAPIView.as_view(),name='linkdeliverytoorder')
]
