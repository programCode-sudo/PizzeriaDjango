from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Authentication.models import BaseUser
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

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
    Vista para obtener todos los usuarios con paginación.
    """

    def get(self, request, *args, **kwargs):
        # Obtén todos los usuarios, ordenados por el campo 'id'
        users = BaseUser.objects.all().order_by('id')  # Ordenamos por 'id', pero puedes elegir otro campo

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