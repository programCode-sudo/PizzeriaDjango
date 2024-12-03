# Order_Manager/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Pedidos.models import Pedido
from .serializer import PedidoSerializer,PedidoSerializerPersonalizado
from Delivery_Person.models import Delivery_Person
from Delivery_Person.serializers import DeliveryPersonSerializer
from RestauranteAPI.customPagination import CustomPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import serializers

class CreatePedidoAPIView(APIView):

    @swagger_auto_schema(
        operation_description="Crear un nuevo pedido en el sistema. pasa una lista de ids de fooditems",
        request_body=PedidoSerializer,
        responses={
            201: openapi.Response(
                description="Pedido creado con éxito",
                schema=PedidoSerializer
            ),
            400: openapi.Response(
                description="Error al crear el pedido",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción del error')
                    }
                )
            ),
        }
    )

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

    @swagger_auto_schema(
        operation_description="Obtener todos los pedidos en el sistema, con paginación.",
        responses={
            200: openapi.Response(
                description="Lista de pedidos paginada.",
                schema=PedidoSerializerPersonalizado(many=True)
            ),
            400: openapi.Response(
                description="Error al obtener los pedidos.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción del error')
                    }
                )
            )
        }
    )

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

    @swagger_auto_schema(
        operation_description="Cancelar un pedido mediante su ID.",
        responses={
            200: openapi.Response(
                description="Pedido cancelado con éxito.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito')
                    }
                )
            ),
            400: openapi.Response(
                description="El pedido ya está cancelado o no se encuentra.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
            404: openapi.Response(
                description="Pedido no encontrado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter('pedido_id', openapi.IN_PATH, description="ID del pedido a cancelar", type=openapi.TYPE_INTEGER)
        ]
    )

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

    @swagger_auto_schema(
        operation_description="Borrar un pedido cancelado mediante su ID.",
        responses={
            200: openapi.Response(
                description="Pedido borrado con éxito.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito')
                    }
                )
            ),
            400: openapi.Response(
                description="El pedido no está cancelado o no puede ser borrado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
            404: openapi.Response(
                description="Pedido no encontrado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter('pedido_id', openapi.IN_PATH, description="ID del pedido a borrar", type=openapi.TYPE_INTEGER)
        ]
    )

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

    @swagger_auto_schema(
        operation_description="Obtener detalles de un pedido mediante su ID.",
        responses={
            200: openapi.Response(
                description="Detalles del pedido.",
                schema=PedidoSerializerPersonalizado()
            ),
            404: openapi.Response(
                description="Pedido no encontrado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter('pedido_id', openapi.IN_PATH, description="ID del pedido", type=openapi.TYPE_INTEGER)
        ]
    )

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

    @swagger_auto_schema(
        operation_description="Obtener todos los pedidos filtrados por el estado.",
        responses={
            200: openapi.Response(
                description="Lista de pedidos filtrados por estado.",
                schema=PedidoSerializerPersonalizado(many=True)
            ),
            400: openapi.Response(
                description="No se proporcionó un estado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
            404: openapi.Response(
                description="No se encontraron pedidos con el estado proporcionado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            )
        },
        manual_parameters=[
            openapi.Parameter('status', openapi.IN_QUERY, description="Estado de los pedidos a filtrar", type=openapi.TYPE_STRING)
        ]
    )

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

    @swagger_auto_schema(
        operation_description="Obtiene la lista de repartidores filtrada por su estado online.",
        responses={
            200: openapi.Response('Lista de repartidores', DeliveryPersonSerializer),
            400: 'Debe proporcionar el estado is_online (True o False).',
            500: 'Error al obtener los repartidores.'
        },
        manual_parameters=[
            openapi.Parameter('is_online', openapi.IN_QUERY, description="Estado online del repartidor", type=openapi.TYPE_BOOLEAN)
        ]
    )

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

    @swagger_auto_schema(
        operation_description="Obtiene la lista paginada de repartidores filtrada por su estado online.",
        responses={
            200: openapi.Response('Lista paginada de repartidores', DeliveryPersonSerializer),
            400: 'Debe proporcionar el estado is_online (True o False).',
            500: 'Error al obtener los repartidores.'
        },
        manual_parameters=[
            openapi.Parameter('is_online', openapi.IN_QUERY, description="Estado online del repartidor", type=openapi.TYPE_BOOLEAN)
        ]
    )

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

    @swagger_auto_schema(
        operation_description="Asocia un repartidor a un pedido.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['pedido_id', 'delivery_person_id'],
            properties={
                'pedido_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del pedido'),
                'delivery_person_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del repartidor')
            }
        ),
        responses={
            200: openapi.Response(description="Pedido asociado exitosamente al repartidor.", schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito')
                }
            )),
            400: openapi.Response(description="Debe proporcionar tanto el ID del pedido como el del repartidor, o el pedido ya tiene un repartidor asignado."),
            404: openapi.Response(description="Pedido o repartidor no encontrado."),
            500: openapi.Response(description="Error al asociar el repartidor al pedido.")
        }
    )

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






