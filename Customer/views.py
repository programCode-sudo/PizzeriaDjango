from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Cart, CartItem, Customer,LoyaltyPoint,Coupon
from .serializers import CartItemSerializer
from RestauranteData.models import FoodItem
from rest_framework.permissions import IsAuthenticated

class AddToCartView(APIView):
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

    def post(self, request, customer_id, *args, **kwargs):
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Cliente no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Obtener la cantidad de puntos del cuerpo de la solicitud
        points_to_add = request.data.get("points", 0)
        if not isinstance(points_to_add, int) or points_to_add <= 0:
            return Response({"error": "La cantidad de puntos debe ser un entero positivo"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear un registro de puntos
        LoyaltyPoint.objects.create(customer=customer, points=points_to_add)

        # Calcular los puntos totales no expirados
        total_points = sum(
            point.points for point in customer.loyalty_points.all() if not point.is_expired()
        )

        return Response({
            "message": "Puntos añadidos exitosamente",
            "total_points": total_points
        }, status=status.HTTP_200_OK)

class DeleteLoyaltyPointsView(APIView):
    permission_classes = [IsAuthenticated]

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
