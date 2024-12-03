from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Cart, CartItem, Customer,LoyaltyPoint,Coupon
from .serializers import CartItemSerializer,CustomerProfileSerializer
from RestauranteData.models import FoodItem
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AddToCartView(APIView):

    @swagger_auto_schema(
        operation_description="Agrega un item al carrito del cliente. Si el item ya existe, se actualiza la cantidad.",
        manual_parameters=[
            openapi.Parameter(
                'Authorization', 
                openapi.IN_HEADER, 
                description="Token JWT Bearer", 
                type=openapi.TYPE_STRING, 
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'food_item': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del item de comida a agregar al carrito.'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Cantidad del item de comida a agregar al carrito.')
            },
            required=['food_item', 'quantity']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Item agregado exitosamente al carrito.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito.')
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Error en la solicitud (por ejemplo, item de comida no existe o cantidad no válida).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error.')
                    }
                )
            )
        }
    )

    def post(self, request, *args, **kwargs):
        customer = request.user.customer  # Asumiendo que el usuario está autenticado
        food_item_id = request.data.get('food_item')
        quantity = request.data.get('quantity')

         # Asegurarse de que quantity es un entero
        try:
            quantity = int(quantity)  # Convertir quantity a un entero
        except ValueError:
            return Response({"detail": "La cantidad debe ser un número entero válido."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el FoodItem existe
        try:
            food_item = FoodItem.objects.get(id=food_item_id)
        except FoodItem.DoesNotExist:
            return Response({"detail": "El item de comida no existe."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el cliente tiene un carrito
        try:
            cart = Cart.objects.get(customer=customer)
        except Cart.DoesNotExist:
            return Response({"detail": "El cliente no tiene un carrito."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si ya existe un CartItem con este FoodItem
        cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)
        if not created:
            # Si ya existe, actualizar la cantidad
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # Si no existe, establecer la cantidad inicial
            cart_item.quantity = quantity
            cart_item.save()

        return Response({"detail": "Item agregado al carrito exitosamente."}, status=status.HTTP_200_OK)

class GetCartItemsView(APIView):

    permission_classes = [IsAuthenticated]  # Asegura que el usuario esté autenticado

    @swagger_auto_schema(
        operation_description="Obtiene todos los items del carrito de un cliente autenticado.",
        manual_parameters=[
            openapi.Parameter(
                'Authorization', 
                openapi.IN_HEADER, 
                description="Token JWT Bearer", 
                type=openapi.TYPE_STRING, 
                required=True
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Items del carrito, puntos y cupones disponibles.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'cart_items': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del item de comida'),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING, description='Descripción del item de comida'),
                                    'category': openapi.Schema(type=openapi.TYPE_STRING, description='Categoría del item'),
                                    'unitPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description='Precio unitario'),
                                    'stockRestaurant': openapi.Schema(type=openapi.TYPE_INTEGER, description='Stock disponible en el restaurante'),
                                    'image': openapi.Schema(type=openapi.TYPE_STRING, description='URL de la imagen del item'),
                                    'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Cantidad en el carrito'),
                                    'totalPrice': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description='Precio total por cantidad')
                                }
                            )
                        ),
                        'total_points': openapi.Schema(type=openapi.TYPE_INTEGER, description='Puntos de lealtad disponibles'),
                        'available_coupons': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del cupón'),
                                    'discount_amount': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description='Monto de descuento del cupón'),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, description='Fecha de creación del cupón'),
                                }
                            )
                        )
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Error en la solicitud (por ejemplo, carrito no encontrado).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error.')
                    }
                )
            )
        }
    )

    def get(self, request, *args, **kwargs):
        # Obtener el usuario actual desde el token
        user = request.user
        
        try:
            # Acceder al cliente y carrito
            customer = user.customer
            cart = Cart.objects.get(customer=customer)
        except Cart.DoesNotExist:
            return Response({"detail": "El cliente no tiene un carrito."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener todos los items del carrito
        cart_items = CartItem.objects.filter(cart=cart)
        
        # Crear una lista de los datos del FoodItem para cada CartItem
        items_data = []
        for cart_item in cart_items:
            food_item = cart_item.food_item
            items_data.append({
                "name": food_item.name,
                "description": food_item.description,
                "category": food_item.category,
                "unitPrice": food_item.unitPrice,
                "stockRestaurant": food_item.stockRestaurant,
                "image": food_item.image.url if food_item.image else None,
                "quantity": cart_item.quantity,
                "totalPrice": cart_item.quantity * food_item.unitPrice
            })

        # Calcular puntos totales (excluyendo los expirados)
        total_points = sum(
            point.points for point in customer.loyalty_points.all() if not point.is_expired()
        )

        # Obtener los cupones válidos (excluyendo los expirados)
        coupons = [
            {
                "id": coupon.id,
                "discount_amount": coupon.discount_amount,
                "created_at": coupon.created_at,
            }
            for coupon in customer.coupons.all() if not coupon.is_expired()
        ]

        # Respuesta extendida
        return Response({
            "cart_items": items_data,
            "total_points": total_points,
            "available_coupons": coupons,
        }, status=status.HTTP_200_OK)

class DeleteCartItemByFoodNameView(APIView):
    permission_classes = [IsAuthenticated]  # Asegura que el usuario esté autenticado
    
    @swagger_auto_schema(
        operation_description="Elimina un item del carrito del usuario por su nombre.",
        manual_parameters=[
            openapi.Parameter(
                'Authorization', 
                openapi.IN_HEADER, 
                description="Token JWT Bearer", 
                type=openapi.TYPE_STRING, 
                required=True
            ),
            openapi.Parameter(
                'food_item_name', 
                openapi.IN_PATH, 
                description="Nombre del item de comida a eliminar", 
                type=openapi.TYPE_STRING, 
                required=True
            ),
        ],
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(description="Item de carrito eliminado exitosamente."),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Error en la solicitud (por ejemplo, el carrito o el item no existen).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error.')
                    }
                )
            )
        }
    )
    
    def delete(self, request, food_item_name, *args, **kwargs):
        # Obtener el usuario actual desde el token
        user = request.user

        # Intentar obtener el perfil del cliente
        try:
            customer = user.customer  # Acceder al perfil de cliente
        except AttributeError:
            return Response({"detail": "El usuario no tiene un perfil de cliente."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Intentar obtener el carrito del usuario
        try:
            cart = Cart.objects.get(customer=customer)
        except Cart.DoesNotExist:
            return Response({"detail": "El cliente no tiene un carrito."}, status=status.HTTP_400_BAD_REQUEST)

        # Intentar obtener el FoodItem por el nombre
        try:
            food_item = FoodItem.objects.get(name=food_item_name)
        except FoodItem.DoesNotExist:
            return Response({"detail": "El item de comida con ese nombre no existe."}, status=status.HTTP_400_BAD_REQUEST)

        # Intentar obtener el CartItem correspondiente al FoodItem en el carrito
        try:
            cart_item = CartItem.objects.get(cart=cart, food_item=food_item)
        except CartItem.DoesNotExist:
            return Response({"detail": "El item de carrito no existe."}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar el CartItem
        cart_item.delete()

        # Retornar una respuesta exitosa
        return Response({"detail": "El item de carrito ha sido eliminado."}, status=status.HTTP_204_NO_CONTENT)

class AddLoyaltyPointsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Añade puntos de lealtad a un cliente.",
        manual_parameters=[
            openapi.Parameter(
                'Authorization', 
                openapi.IN_HEADER, 
                description="Token JWT Bearer", 
                type=openapi.TYPE_STRING, 
                required=True
            ),
            openapi.Parameter(
                'customer_id', 
                openapi.IN_PATH, 
                description="ID del cliente al que se le añadirán los puntos", 
                type=openapi.TYPE_INTEGER, 
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'points': openapi.Schema(type=openapi.TYPE_INTEGER, description='Cantidad de puntos a añadir')
            },
            required=['points']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Puntos añadidos exitosamente.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito'),
                        'total_points': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total de puntos del cliente')
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Error en la solicitud (por ejemplo, cantidad de puntos no válida).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={ 
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Cliente no encontrado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={ 
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            )
        }
    )

    def post(self, request, customer_id, *args, **kwargs):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Obtener la cantidad de puntos del cuerpo de la solicitud
        points_to_add = request.data.get("points", 0)
        if not isinstance(points_to_add, int) or points_to_add <= 0:
            return Response({"error": "La cantidad de puntos debe ser un entero positivo"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si el cliente ya tiene un registro de LoyaltyPoint
        loyalty_point, created = LoyaltyPoint.objects.get_or_create(customer=customer, defaults={"points": 0})

        # Si ya existía, suma los nuevos puntos al registro actual
        loyalty_point.points += points_to_add
        loyalty_point.save()

        return Response({
            "message": "Puntos añadidos exitosamente",
            "total_points": loyalty_point.points
        }, status=status.HTTP_200_OK)

class DeleteLoyaltyPointsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Elimina todos los puntos de lealtad de un cliente.",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Puntos eliminados exitosamente.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito'),
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Cliente no encontrado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
        }
    )

    def delete(self, request, customer_id, *args, **kwargs):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Eliminar todos los puntos asociados al cliente
        customer.loyalty_points.all().delete()

        return Response({
            "message": "Puntos eliminados exitosamente"
        }, status=status.HTTP_200_OK)

class CreateCouponView(APIView):

    @swagger_auto_schema(
        operation_description="Crea un cupón de descuento para un cliente.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'discount_amount': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description='Monto de descuento'),
            },
            required=['discount_amount']
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Cupón creado con éxito.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito'),
                        'coupon': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID del cupón'),
                                'discount_amount': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description='Monto de descuento'),
                                'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Fecha de expiración del cupón'),
                            }
                        )
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Cliente no encontrado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
        }
    )

    def post(self, request, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        discount_amount = request.data.get('discount_amount', 10.00)  # Descuento por defecto: 10 USD
        
        try:
            # Obtener al cliente
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"detail": "Cliente no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        # Crear el cupón
        coupon = Coupon.objects.create(
            customer=customer,
            discount_amount=discount_amount
        )
        return Response({
            "detail": "Cupón creado con éxito.",
            "coupon": {
                "id": coupon.id,
                "discount_amount": coupon.discount_amount,
                "expires_at": coupon.expires_at,
            }
        }, status=status.HTTP_201_CREATED)
    
class DeleteCouponView(APIView):

    @swagger_auto_schema(
        operation_description="Elimina un cupón específico de un cliente.",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Cupón eliminado con éxito.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito')
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description="Cupón no encontrado.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
        }
    )

    def delete(self, request, *args, **kwargs):
        coupon_id = kwargs.get('coupon_id')
        
        try:
            # Obtener el cupón
            coupon = Coupon.objects.get(id=coupon_id)
        except Coupon.DoesNotExist:
            return Response({"detail": "Cupón no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        # Eliminar el cupón
        coupon.delete()
        return Response({"detail": "Cupón eliminado con éxito."}, status=status.HTTP_200_OK)

class AssignPhoneNumberView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Asigna un número de teléfono a un cliente. Requiere Berar Token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Número de teléfono del cliente')
            },
            required=['phone']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Número de teléfono asignado exitosamente.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito')
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Error con la solicitud (número de teléfono inválido).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
        }
    )

    def post(self, request, *args, **kwargs):
        user = request.user

        # Verificar si el usuario tiene un perfil de cliente
        try:
            customer = user.customer
        except AttributeError:
            return Response({"detail": "El usuario no tiene un perfil de cliente."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el número de teléfono del cuerpo de la solicitud
        phone_number = request.data.get("phone", "")

        # Verificar que el número de teléfono tenga exactamente 8 dígitos y sea un número
        if not phone_number.isdigit() or len(phone_number) != 8:
            return Response({"detail": "El número de teléfono debe tener exactamente 8 dígitos."}, status=status.HTTP_400_BAD_REQUEST)

        # Asignar el número de teléfono al perfil del cliente
        customer.phone = phone_number
        customer.save()

        return Response({"detail": "Número de teléfono asignado exitosamente."}, status=status.HTTP_200_OK)

class AssignAddressView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Asigna una dirección a un cliente. requiere Bearer TOKEN",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'address': openapi.Schema(type=openapi.TYPE_STRING, description='Dirección del cliente')
            },
            required=['address']
        ),
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Dirección asignada exitosamente.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de éxito')
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Error con la solicitud (dirección vacía).",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
        }
    )

    def post(self, request, *args, **kwargs):
        user = request.user

        # Verificar si el usuario tiene un perfil de cliente
        try:
            customer = user.customer
        except AttributeError:
            return Response({"detail": "El usuario no tiene un perfil de cliente."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener la dirección del cuerpo de la solicitud
        address = request.data.get("address", "")

        # Verificar que la dirección no esté vacía
        if not address:
            return Response({"detail": "La dirección no puede estar vacía."}, status=status.HTTP_400_BAD_REQUEST)

        # Asignar la dirección al perfil del cliente
        customer.customer_addres = address
        customer.save()

        return Response({"detail": "Dirección asignada exitosamente."}, status=status.HTTP_200_OK)

class CustomerProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Obtiene el perfil del cliente.",
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Perfil del cliente obtenido exitosamente.",
                schema=CustomerProfileSerializer
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Error con la solicitud.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Mensaje de error')
                    }
                )
            ),
        }
    )

    def get(self, request, *args, **kwargs):
        user = request.user

        # Verificar si el usuario tiene un perfil de cliente
        try:
            customer = user.customer
        except AttributeError:
            return Response({"detail": "El usuario no tiene un perfil de cliente."}, status=status.HTTP_400_BAD_REQUEST)

        # Serializar los datos del perfil del cliente
        serializer = CustomerProfileSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)
