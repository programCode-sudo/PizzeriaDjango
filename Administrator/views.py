from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Authentication.models import BaseUser
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from RestauranteData.models import Restaurante
from Authentication.serializers import RegisterSerializer,EditUserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class DeleteUserView(APIView):
    """
    Vista para eliminar usuarios con roles específicos.
    """
    @swagger_auto_schema(
        operation_description="Elimina un usuario por su username y email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre de usuario del usuario a eliminar'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email del usuario a eliminar'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, description='Rol del usuario a eliminar'),
            }
        ),
        responses={
            200: openapi.Response('Usuario eliminado exitosamente'),
            400: openapi.Response('Error al eliminar usuario'),
        }
    )


    def post(self, request, *args, **kwargs):
        # Obtén los datos enviados desde el frontend
        username = request.data.get("username")
        role = request.data.get("role")
        email = request.data.get("email")

        # no se intente eliminar un usuario "customer"
        if role == "customer":
            return Response(
                {"error": "No se puede eliminar un usuario con el rol de 'customer'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Busca el usuario por username y email
        user = get_object_or_404(BaseUser, username=username, email=email)

        # Elimina el usuario
        user.delete()

        return Response(
            {"success": "Usuario eliminado exitosamente"},
            status=status.HTTP_200_OK,
        )

class GetAllUsersView(APIView):
    """
    Vista para obtener todos los usuarios con paginación, excluyendo a los usuarios con rol 'customer'.
    """
    @swagger_auto_schema(
        operation_description="Obtiene todos los usuarios, excluyendo a los que tienen rol 'customer'.",
        responses={
            200: openapi.Response(
                'Lista de usuarios excluyendo los de rol "customer".',
                openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'role': openapi.Schema(type=openapi.TYPE_STRING)
                    })
                )
            ),
            400: openapi.Response('Error al obtener los usuarios'),
        }
    )


    def get(self, request, *args, **kwargs):
        # Filtrar usuarios que no tienen rol 'customer'
        users = BaseUser.objects.exclude(role='customer').order_by('id')  # Excluir a los usuarios con rol 'customer'

        # Paginación
        paginator = PageNumberPagination()
        paginator.page_size = 5  # Número de usuarios por página
        result_page = paginator.paginate_queryset(users, request)

        # Serializar los resultados
        user_data = [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            } for user in result_page
        ]

        return paginator.get_paginated_response(user_data)

class GetUserByIdView(APIView):
    """
    Vista para obtener un solo usuario por su 'id', excluyendo los usuarios con rol 'customer'.
    """

    @swagger_auto_schema(
        operation_description="Obtiene un usuario específico por su ID, excluyendo los usuarios con rol 'customer'.",
        responses={
            200: openapi.Response(
                'Usuario encontrado por ID.',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'role': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response('Usuario no encontrado'),
        }
    )


    def get(self, request, user_id, *args, **kwargs):
        try:
            # Obtener usuario por id, excluyendo aquellos con rol 'customer'
            user = BaseUser.objects.exclude(role='customer').get(id=user_id)
            
            # Serializar el usuario
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            }
            
            return Response(user_data, status=status.HTTP_200_OK)
        except BaseUser.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
class GetUserByUsernameView(APIView):
    """
    Vista para obtener un solo usuario por su 'username', excluyendo los usuarios con rol 'customer'.
    """
    @swagger_auto_schema(
        operation_description="Obtiene un usuario específico por su username, excluyendo los usuarios con rol 'customer'.",
        responses={
            200: openapi.Response(
                'Usuario encontrado por username.',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'username': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'role': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: openapi.Response('Usuario no encontrado'),
        }
    )

    def get(self, request, username, *args, **kwargs):
        try:
            # Obtener usuario por username, excluyendo aquellos con rol 'customer'
            user = BaseUser.objects.exclude(role='customer').get(username=username)
            
            # Serializar el usuario
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            }
            
            return Response(user_data, status=status.HTTP_200_OK)
        except BaseUser.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
class EditUserView(APIView):
    """
    Vista para editar un usuario basado en su 'id', excluyendo los usuarios con rol 'customer'.
    """
    @swagger_auto_schema(
        operation_description="Edita un usuario por su ID, excluyendo los usuarios con rol 'customer'.",
        request_body=EditUserSerializer,
        responses={
            200: openapi.Response(
                'Usuario actualizado.',
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'username': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'role': openapi.Schema(type=openapi.TYPE_STRING),
                        })
                    }
                )
            ),
            400: openapi.Response('Error al actualizar el usuario'),
            404: openapi.Response('Usuario no encontrado o no editable'),
        }
    )


    def put(self, request, user_id, *args, **kwargs):
        try:
            # Obtener usuario por id, excluyendo aquellos con rol 'customer'
            user = BaseUser.objects.exclude(role='customer').get(id=user_id)
        except BaseUser.DoesNotExist:
            return Response({"error": "Usuario no encontrado o no editable (rol customer)"}, status=status.HTTP_404_NOT_FOUND)

        # Serializar el usuario con los nuevos datos
        serializer = EditUserSerializer(user, data=request.data, partial=True)  # 'partial=True' permite actualizaciones parciales

        if serializer.is_valid():
            updated_user = serializer.save()  # Guardar los cambios

            # Retornar la respuesta con los datos actualizados
            user_data = {
                'id': updated_user.id,
                'username': updated_user.username,
                'email': updated_user.email,
                'first_name': updated_user.first_name,
                'last_name': updated_user.last_name,
                'role': updated_user.role,  # El rol sigue sin cambios
            }
            return Response({"message": "Usuario actualizado exitosamente", "user": user_data}, status=status.HTTP_200_OK)
        
        # Si los datos no son válidos, devolver los errores
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ToggleLoyaltyPointsView(APIView):
    """
    Vista para activar o desactivar los puntos de lealtad en un restaurante.
    """
    @swagger_auto_schema(
        operation_description="Activa o desactiva los puntos de lealtad de un restaurante.",
        responses={
            200: openapi.Response(
                description="Operación exitosa",
                examples={
                    "application/json": {
                        "message": "Puntos de lealtad activados.",
                        "lealtad_points": True
                    }
                }
            ),
            404: openapi.Response(
                description="Restaurante no encontrado.",
                examples={
                    "application/json": {
                        "error": "Restaurante no encontrado."
                    }
                }
            ),
        },
        request_body=None,
    )


    def post(self, request, restaurante_id, *args, **kwargs):
        try:
            # Obtener el restaurante por ID
            restaurante = Restaurante.objects.get(id=restaurante_id)
        except Restaurante.DoesNotExist:
            return Response({"error": "Restaurante no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        # Alternar el estado de los puntos de lealtad
        restaurante.lealtad_points = not restaurante.lealtad_points
        restaurante.save()

        return Response(
            {"message": f"Puntos de lealtad {'activados' if restaurante.lealtad_points else 'desactivados'}.", 
             "lealtad_points": restaurante.lealtad_points},
            status=status.HTTP_200_OK
        )

class ToggleCuponsView(APIView):
    """
    Vista para activar o desactivar los cupones en un restaurante.
    """
    @swagger_auto_schema(
        operation_description="Activa o desactiva los cupones de un restaurante.",
        responses={
            200: openapi.Response(
                description="Operación exitosa",
                examples={
                    "application/json": {
                        "message": "Cupones activados.",
                        "cupons": True
                    }
                }
            ),
            404: openapi.Response(
                description="Restaurante no encontrado.",
                examples={
                    "application/json": {
                        "error": "Restaurante no encontrado."
                    }
                }
            ),
        },
        request_body=None,
    )



    def post(self, request, restaurante_id, *args, **kwargs):
        try:
            # Obtener el restaurante por ID
            restaurante = Restaurante.objects.get(id=restaurante_id)
        except Restaurante.DoesNotExist:
            return Response({"error": "Restaurante no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        # Alternar el estado de los cupones
        restaurante.cupons = not restaurante.cupons
        restaurante.save()

        return Response(
            {"message": f"Cupones {'activados' if restaurante.cupons else 'desactivados'}.", 
             "cupons": restaurante.cupons},
            status=status.HTTP_200_OK
        )