from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Pedidos.models import Pedido
from Delivery_Person.models import Delivery_Person
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Count

class ActualizarEstadoPedidoDispatcherAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    ESTADOS_VALIDOS = ['Listo', 'InDelivery', 'Cocina']

    def post(self, request, pedido_id, *args, **kwargs):
        try:
            # Obtener el pedido por el ID
            pedido = Pedido.objects.get(id=pedido_id)

            # Obtener el nuevo estado desde el cuerpo de la solicitud
            nuevo_estado = request.data.get('status', None)

            # Validar que el nuevo estado sea uno de los estados válidos
            if nuevo_estado not in self.ESTADOS_VALIDOS:
                return Response({'message': f'Estado inválido. Los estados válidos son: {", ".join(self.ESTADOS_VALIDOS)}.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validar el cambio de estado según las reglas especificadas
            if pedido.status == 'Pendiente' and nuevo_estado != 'Cocina':
                return Response({'message': 'El pedido solo puede cambiar de Pendiente a Cocina.'}, status=status.HTTP_400_BAD_REQUEST)
            if pedido.status == 'Cocina' and nuevo_estado not in ['Listo', 'InDelivery']:
                return Response({'message': 'El pedido en Cocina solo puede cambiar a Listo o InDelivery.'}, status=status.HTTP_400_BAD_REQUEST)

            # Si el nuevo estado es InDelivery y el estado actual es Cocina, asignar un repartidor
            if pedido.status == 'Cocina' and nuevo_estado == 'InDelivery':
                # Buscar un repartidor online con menos pedidos asignados
                delivery_person = Delivery_Person.objects.filter(is_online=True)\
                                        .annotate(num_pedidos=Count('pedido'))\
                                        .order_by('num_pedidos').first()

                if not delivery_person:
                    return Response({'message': 'No hay repartidores disponibles en línea.'}, status=status.HTTP_400_BAD_REQUEST)

                pedido.delivery_person = delivery_person

            # Cambiar el estado del pedido
            pedido.status = nuevo_estado
            pedido.save()

            message = f'Estado del pedido {pedido_id} actualizado a {nuevo_estado} con éxito.'
            if nuevo_estado == 'InDelivery':
                message += f' Asignado al repartidor {pedido.delivery_person.user.username}.'

            return Response({'message': message}, status=status.HTTP_200_OK)

        except Pedido.DoesNotExist:
            return Response({'message': 'El pedido no existe.'}, status=status.HTTP_404_NOT_FOUND)
