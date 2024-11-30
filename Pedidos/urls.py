from django.urls import path
from .views import ProcesarPedidoAPIView,VerPedidoAPIView,ListUserOrdersView,CancelOrderView,DeleteOrderView

urlpatterns = [
    path('userCartToOrder/',ProcesarPedidoAPIView.as_view(),name='usercartorder'),
    path('viewOrderUser/<int:pedido_id>/',VerPedidoAPIView.as_view(),name='viewOrderUser'),
    path('listUserOrders/',ListUserOrdersView.as_view(),name='listuserorders'),
    path('cancelOrderUser/<int:order_id>/',CancelOrderView.as_view(),name='cancelorderuser'),
    path('deleteOrderUser/<int:order_id>/',DeleteOrderView.as_view(),name='deleteorderuser'),

]
