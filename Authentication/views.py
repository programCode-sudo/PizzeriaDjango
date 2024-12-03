#Authentication/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterView(APIView):
    """
    Vista para registrar nuevos usuarios.
    """
    @swagger_auto_schema(
        operation_description="Register a new user and generate access tokens.",
        responses={
            201: openapi.Response(
                description="User registered successfully.",
                schema=RegisterSerializer()
            ),
            400: "Bad request",
        },
        request_body=RegisterSerializer
    )


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
                        "first_name": user.first_name,
                        "last_name": user.last_name,
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
    @swagger_auto_schema(
        operation_description="Authenticate a user and provide JWT tokens.",
        responses={
            200: openapi.Response(
                description="Login successful.",
                schema=RegisterSerializer()  # You may want to create a custom serializer for login response
            ),
            400: "Bad request",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            }
        )
    )

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
                "user": {
                    "id":user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                },
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )