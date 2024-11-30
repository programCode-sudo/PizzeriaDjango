# Order_Manager/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Pedidos.models import Pedido
from .serializer import PedidoSerializer,PedidoSerializerPersonalizado
from Delivery_Person.models import Delivery_Person
from Delivery_Person.serializers import DeliveryPersonSerializer
from RestauranteAPI.customPagination import CustomPageNumberPagination
class CreatePedidoAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PedidoSerializer(data=request.data)
        if serializer.is_valid():
            pedido = serializer.save()
            return Response({
                'message': 'Pedido creado con éxito',
                'pedido_id': pedido.id,
                'total': str(pedido.Total)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListarPedidosAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Obtener todos los pedidos
        pedidos = Pedido.objects.all()
        
        # Paginación
        paginator = CustomPageNumberPagination()
        paginated_pedidos = paginator.paginate_queryset(pedidos, request)
        
        # Serializar los pedidos
        serializer = PedidoSerializerPersonalizado(paginated_pedidos, many=True)
        
        # Devolver los resultados paginados
        return paginator.get_paginated_response(serializer.data)
    
class CancelarPedidoAPIView(APIView):
    def post(self, request, pedido_id, *args, **kwargs):
        try:
            # Obtener el pedido
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Verificar si ya está cancelado
            if pedido.status == 'Cancelado':
                return Response({'message': 'El pedido ya está cancelado.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Cambiar el estado a "Cancelado"
            pedido.status = 'Cancelado'
            pedido.save()
            return Response({'message': 'Pedido cancelado con éxito.'}, status=status.HTTP_200_OK)
        
        except Pedido.DoesNotExist:
            return Response({'message': 'El pedido no existe.'}, status=status.HTTP_404_NOT_FOUND)

class BorrarPedidoAPIView(APIView):
    def delete(self, request, pedido_id, *args, **kwargs):
        try:
            # Obtener el pedido
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Verificar si está cancelado
            if pedido.status != 'Cancelado':
                return Response({'message': 'No se puede borrar el pedido. Primero debe ser cancelado.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Eliminar el pedido
            pedido.delete()
            return Response({'message': 'Pedido borrado con éxito.'}, status=status.HTTP_200_OK)
        
        except Pedido.DoesNotExist:
            return Response({'message': 'El pedido no existe.'}, status=status.HTTP_404_NOT_FOUND)

class VerPedidoDetalladoAPIView(APIView):
    def get(self, request, pedido_id, *args, **kwargs):
        try:
            # Obtener el pedido
            pedido = Pedido.objects.get(id=pedido_id)
            
            # Serializar el pedido
            serializer = PedidoSerializerPersonalizado(pedido)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Pedido.DoesNotExist:
            return Response({'message': 'El pedido no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
class ListarPedidosPorEstadoAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Obtener el estado enviado desde el front
        estado = request.query_params.get('status', None)
        
        if not estado:
            return Response({'message': 'Debe proporcionar un estado.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrar los pedidos por el estado proporcionado
        pedidos = Pedido.objects.filter(status=estado)
        
        if not pedidos.exists():
            return Response({'message': f'No hay pedidos con el estado: {estado}.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Paginación
        paginator = CustomPageNumberPagination()
        paginated_pedidos = paginator.paginate_queryset(pedidos, request)
        
        # Serializar los pedidos
        serializer = PedidoSerializerPersonalizado(paginated_pedidos, many=True)
        
        # Devolver los resultados paginados
        return paginator.get_paginated_response(serializer.data)

class ListarRepartidoresAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Obtener el parámetro 'is_online' de la solicitud
        is_online = request.query_params.get('is_online', None)
        
        if is_online is None:
            return Response({'message': 'Debe proporcionar el estado is_online (True o False).'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            is_online = bool(int(is_online))  # Convertir el parámetro a un valor booleano
        except ValueError:
            return Response({'message': 'El parámetro is_online debe ser 1 (True) o 0 (False).'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrar los repartidores por el estado is_online
        repartidores = Delivery_Person.objects.filter(is_online=is_online)
        
        # Serializar los datos de los repartidores
        serializer = DeliveryPersonSerializer(repartidores, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ListarRepartidoresPaginationAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Obtener el parámetro 'is_online' de la solicitud
        is_online = request.query_params.get('is_online', None)
        
        if is_online is None:
            return Response({'message': 'Debe proporcionar el estado is_online (True o False).'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            is_online = bool(int(is_online))  # Convertir el parámetro a un valor booleano
        except ValueError:
            return Response({'message': 'El parámetro is_online debe ser 1 (True) o 0 (False).'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrar los repartidores por el estado is_online
        repartidores = Delivery_Person.objects.filter(is_online=is_online)
        
        # Aplicar paginación
        paginator = CustomPageNumberPagination()
        paginated_repartidores = paginator.paginate_queryset(repartidores, request)
        
        # Serializar los datos de los repartidores
        serializer = DeliveryPersonSerializer(paginated_repartidores, many=True)
        
        # Devolver los datos paginados
        return paginator.get_paginated_response(serializer.data)
    
class AsociarRepartidorAPedidoAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Obtener los IDs del pedido y del repartidor desde los datos de la solicitud
        pedido_id = request.data.get('pedido_id', None)
        delivery_person_id = request.data.get('delivery_person_id', None)
        
        # Verificar si ambos IDs han sido proporcionados
        if not pedido_id or not delivery_person_id:
            return Response({'message': 'Debe proporcionar tanto el ID del pedido como el del repartidor.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Obtener el pedido y el repartidor
            pedido = Pedido.objects.get(id=pedido_id)
            repartidor = Delivery_Person.objects.get(id=delivery_person_id)

            # Verificar si el pedido ya tiene un repartidor asignado
            if pedido.delivery_person is not None:
                return Response({'message': f'El pedido {pedido_id} ya tiene un repartidor asignado.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar si el pedido está en estado "Listo" y no en estado "Cancelado"
            if pedido.status != 'Listo':
                return Response({'message': 'El pedido no está listo para entrega.'}, status=status.HTTP_400_BAD_REQUEST)
            if pedido.status == 'Cancelado':
                return Response({'message': 'El pedido está cancelado y no puede ser asignado a un repartidor.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Asociar el repartidor al pedido y actualizar el estado del pedido a "InDelivery"
            pedido.delivery_person = repartidor
            pedido.status = 'InDelivery'
            pedido.save()
            
            return Response({'message': f'Pedido {pedido_id} asociado con éxito al repartidor {repartidor.user.username}.'}, status=status.HTTP_200_OK)
        
        except Pedido.DoesNotExist:
            return Response({'message': 'El pedido no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Delivery_Person.DoesNotExist:
            return Response({'message': 'El repartidor no existe.'}, status=status.HTTP_404_NOT_FOUND)
