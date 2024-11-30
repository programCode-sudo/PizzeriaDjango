from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Delivery_Person
from rest_framework.exceptions import NotFound
from Pedidos.models import Pedido
from Order_Manager.serializer import PedidoSerializerPersonalizado
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from Customer.models import Coupon,LoyaltyPoint,Customer
from rest_framework_simplejwt.authentication import JWTAuthentication
# Create your views here.
class ActualizarEstadoDeliveryPersonAPIView(APIView):
    def post(self, request, delivery_person_id, *args, **kwargs):
        try:
            # Obtener el repartidor por el ID
            delivery_person = Delivery_Person.objects.get(id=delivery_person_id)
            
            # Obtener el valor de is_online desde el cuerpo de la solicitud
            is_online = request.data.get('is_online', None)
            
            # Validar el valor de is_online (debe ser 1 o 0)
            if is_online is None:
                return Response({'message': 'Debe proporcionar el estado is_online (1 o 0).'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                is_online = bool(int(is_online))  # Convertir el valor recibido a booleano
            except ValueError:
                return Response({'message': 'El valor de is_online debe ser 1 (True) o 0 (False).'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar el estado is_online del repartidor
            delivery_person.is_online = is_online
            delivery_person.save()

            return Response({'message': 'Estado de is_online actualizado con éxito.'}, status=status.HTTP_200_OK)

        except Delivery_Person.DoesNotExist:
            raise NotFound({'message': 'El repartidor no existe.'})
        
class VerPedidosPorRepartidorAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        # Asegurarse de que el usuario esté autenticado y que sea un repartidor
        try:
            # Asegurarse de que el usuario tiene un repartidor asociado
            repartidor = request.user.delivery_person  # Suponiendo que hay una relación de uno a uno
            
            # Obtener los pedidos asociados a ese repartidor
            pedidos = Pedido.objects.filter(delivery_person=repartidor)
            
            if not pedidos.exists():
                return Response({'message': f'El repartidor {repartidor.user.username} no tiene pedidos asociados.'}, status=status.HTTP_404_NOT_FOUND)
            
            # Serializar los pedidos
            serializer = PedidoSerializerPersonalizado(pedidos, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Delivery_Person.DoesNotExist:
            return Response({'message': 'El repartidor no está asociado a este usuario.'}, status=status.HTTP_404_NOT_FOUND)

class CambiarEstadoPedidoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    ESTADOS_VALIDOS = ['Cancelado','Entregado']

    def post(self, request, pedido_id, *args, **kwargs):
        try:
            # Obtener el pedido por el ID
            pedido = Pedido.objects.get(id=pedido_id)

            # Verificar que el pedido esté asociado al repartidor autenticado
            if pedido.delivery_person != request.user.delivery_person:
                return Response({'message': 'No tiene permiso para cambiar el estado de este pedido.'}, status=status.HTTP_403_FORBIDDEN)

            # Obtener el nuevo estado desde el cuerpo de la solicitud
            nuevo_estado = request.data.get('status', None)

            # Validar que el nuevo estado sea uno de los estados válidos
            if nuevo_estado not in self.ESTADOS_VALIDOS:
                return Response({'message': f'Estado inválido. Los estados válidos son: {", ".join(self.ESTADOS_VALIDOS)}.'}, status=status.HTTP_400_BAD_REQUEST)

            # Verificar si se está cambiando de InDelivery a Entregado
            cambiar_a_entregado = pedido.status == 'InDelivery' and nuevo_estado == 'Entregado'

            # Cambiar el estado del pedido
            pedido.status = nuevo_estado
            pedido.save()
            print(pedido.status)

            # Verificar si se cambió de InDelivery a Entregado y el pedido tiene un cliente
            if cambiar_a_entregado and pedido.customer_id:
                customer = pedido.customer
                # Incrementar las compras realizadas
                customer.comprasRealizadas += 1
                customer.save()
                print(customer.comprasRealizadas)

                # Crear un cupón si tiene más de 3 compras realizadas
                if customer.comprasRealizadas % 3 == 0:
                    Coupon.objects.create(customer=customer, discount_amount=10.00)
                    print("cupon")

                # Manejar los puntos de lealtad
                loyalty_point, created = LoyaltyPoint.objects.get_or_create(customer=customer, defaults={'points': 0})
                loyalty_point.points += 5
                loyalty_point.save()
                print(loyalty_point.points)

            return Response({'message': f'Estado del pedido {pedido_id} actualizado a {nuevo_estado} con éxito.'}, status=status.HTTP_200_OK)

        except Pedido.DoesNotExist:
            return Response({'message': 'El pedido no existe.'}, status=status.HTTP_404_NOT_FOUND)

class BorrarPedidoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    ESTADOS_ELIMINABLES = ['Cancelado', 'Entregado']

    def delete(self, request, pedido_id, *args, **kwargs):
        try:
            # Obtener el pedido por el ID
            pedido = Pedido.objects.get(id=pedido_id)

            # Verificar que el pedido esté asociado al repartidor autenticado
            if pedido.delivery_person != request.user.delivery_person:
                return Response({'message': 'No tiene permiso para eliminar este pedido.'}, status=status.HTTP_403_FORBIDDEN)

            # Verificar que el estado del pedido sea "Cancelado" o "Entregado"
            if pedido.status not in self.ESTADOS_ELIMINABLES:
                return Response({'message': f'No se puede eliminar el pedido porque su estado es {pedido.status}. Solo se pueden eliminar pedidos con estado Cancelado o Entregado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Eliminar el pedido
            pedido.delete()

            return Response({'message': f'Pedido {pedido_id} eliminado con éxito.'}, status=status.HTTP_204_NO_CONTENT)

        except Pedido.DoesNotExist:
            return Response({'message': 'El pedido no existe.'}, status=status.HTTP_404_NOT_FOUND)
