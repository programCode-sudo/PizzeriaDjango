from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Authentication.models import BaseUser
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from Authentication.serializers import RegisterSerializer,EditUserSerializer

class DeleteUserView(APIView):
    """
    Vista para eliminar usuarios con roles específicos.
    """

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