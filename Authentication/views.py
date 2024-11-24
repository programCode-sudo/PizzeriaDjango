#Authentication/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

class RegisterView(APIView):
    """
    Vista para registrar nuevos usuarios.
    """

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Crea el usuario con el serializador

            # Generar tokens para el usuario registrado
            refresh = RefreshToken.for_user(user)
            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            return Response(
                {
                    "message": "User registered successfully.",
                    "user": {
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    },
                    "tokens": tokens,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Vista para autenticar usuarios y obtener los tokens JWT.
    """

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        # Intentar autenticar al usuario
        user = authenticate(username=username, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid credentials")

        # Generar tokens para el usuario autenticado
        refresh = RefreshToken.for_user(user)
        tokens = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(
            {
                "message": "Login successful.",
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )