from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from Customer.models import Customer,Cart,CartItem,Coupon,LoyaltyPoint
from Pedidos.models import Pedido,PedidoFoodItem
from RestauranteData import Food_Item
from RestauranteData.models import FoodItem
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from Authentication.models import BaseUser
from django.db.models import Sum
from django.shortcuts import get_object_or_404

class ProcesarPedidoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(Customer, user=request.user)

        # Validar número de teléfono
        if not customer.phone:
            return Response({"error": "El cliente debe tener un número de teléfono registrado."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el carrito
        carrito = get_object_or_404(Cart, customer=customer)
        cart_items = CartItem.objects.filter(cart=carrito)

        if not cart_items.exists():
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar dirección
        address = request.data.get("address") or customer.customer_addres
        if not address:
            return Response({"error": "No hay dirección asociada al pedido."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener puntos de lealtad y cupón
        loyalty_points = LoyaltyPoint.objects.filter(customer=customer).first()
        puntos_usar = int(request.data.get("points_to_use", 0))
        coupon_id = request.data.get("coupon_id")

        # Calcular total del carrito
        total = sum(Decimal(item.food_item.unitPrice) * item.quantity for item in cart_items)

        # Verificar stock antes de procesar
        for item in cart_items:
            if item.food_item.stockRestaurant < item.quantity:
                return Response(
                    {"error": f"Stock insuficiente para {item.food_item.name}. Disponibles: {item.food_item.stockRestaurant}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Calcular descuentos pero no aplicarlos aún
        descuento_puntos = 0
        if loyalty_points:
            if puntos_usar > loyalty_points.points:
                return Response({"error": "No tienes suficientes puntos de lealtad."}, status=status.HTTP_400_BAD_REQUEST)
            descuento_puntos = (puntos_usar // 10) * 5  # 10 puntos = 5 dólares

        descuento_cupon = 0
        if coupon_id:
            coupon = get_object_or_404(Coupon, id=coupon_id)
            if coupon.is_expired():
                return Response({"error": "El cupón ha expirado."}, status=status.HTTP_400_BAD_REQUEST)
            descuento_cupon = coupon.discount_amount

        # Verificar total después de aplicar descuentos
        total_final = total - descuento_puntos - descuento_cupon
        if total_final < 5:
            return Response({
                "error": "El precio mínimo de compra es de $5. Ajusta los puntos o no uses el cupón."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Aplicar descuentos definitivos
        if loyalty_points:
            loyalty_points.points -= puntos_usar
            loyalty_points.save()

        if coupon_id:
            coupon.delete()

        # Crear el pedido
        with transaction.atomic():
            pedido = Pedido.objects.create(
                description=f"Pedido de {customer.user.username}",
                address=address,
                status="Pendiente",
                customer=customer,
                Total=total_final
            )

            # Crear elementos del pedido y actualizar stock
            for item in cart_items:
                PedidoFoodItem.objects.create(
                    pedido=pedido,
                    food_item_name=item.food_item.name,
                    food_item_price=item.food_item.unitPrice,
                    quantity=item.quantity,
                    food_item_image=item.food_item.image,
                    food_item_description=item.food_item.description
                )
                item.food_item.stockRestaurant -= item.quantity
                item.food_item.save()

            # Vaciar el carrito
            cart_items.delete()

        return Response({
            "message": "Pedido procesado exitosamente",
            "order_id": pedido.id,
            "total_price": float(total_final)
        }, status=status.HTTP_201_CREATED)

#http://127.0.0.1:8000/pedidos/viewOrderUser/id/
class VerPedidoAPIView(APIView):
    
    def get(self, request, *args, **kwargs):
        # Obtener el cliente autenticado
        customer = get_object_or_404(Customer, user=request.user)

        # Obtener el ID del pedido desde la URL o los parámetros de la solicitud
        pedido_id = kwargs.get("pedido_id")
        pedido = get_object_or_404(Pedido, id=pedido_id, customer=customer)

        # Obtener los elementos de comida asociados con el pedido
        food_items = PedidoFoodItem.objects.filter(pedido=pedido)

        # Crear una lista de los detalles de los items de comida
        food_items_details = [
            {
                "food_item_name": item.food_item_name,
                "food_item_price": item.food_item_price,
                "quantity": item.quantity,
                "food_item_image": item.food_item_image.url if item.food_item_image else None,
                "food_item_description":item.food_item_description
            }
            for item in food_items
        ]

        # Crear el diccionario de respuesta
        response_data = {
            "order_id": pedido.id,
            "customer_id": customer.id,
            "username": customer.user.username,
            "first_name": customer.user.first_name,
            "last_name": customer.user.last_name,
            "email": customer.user.email,
            "phone": customer.phone,
            "address": pedido.address,
            "total_price": str(pedido.Total),  # Aseguramos que el total se pase como string
            "food_items": food_items_details,
            "status": pedido.status
        }

        return Response(response_data, status=status.HTTP_200_OK)

#http://127.0.0.1:8000/pedidos/listUserOrders/
class ListUserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Obtener el cliente autenticado
        customer = get_object_or_404(Customer, user=request.user)

        # Obtener todos los pedidos del cliente
        pedidos = Pedido.objects.filter(customer=customer)

        # Crear la respuesta con la información relevante de los pedidos
        pedidos_data = [
            {
                "order_id": pedido.id,
                "customer_id": customer.id,
                "username": customer.user.username,
                "first_name": customer.user.first_name,
                "last_name": customer.user.last_name,
                "email": customer.user.email,
                "phone": customer.phone,
                "address": pedido.address,
                "total_price": str(pedido.Total),  # Aseguramos que el total se pase como string
                "status": pedido.status
            }
            for pedido in pedidos
        ]

        return Response(pedidos_data, status=status.HTTP_200_OK)
    
#http://127.0.0.1:8000/pedidos/cancelOrderUser/id/
class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Obtener el cliente autenticado
        customer = get_object_or_404(Customer, user=request.user)

        # Obtener el ID del pedido desde la URL o los parámetros de la solicitud
        order_id = kwargs.get("order_id")

        # Obtener el pedido, asegurándose de que pertenezca al cliente autenticado
        pedido = get_object_or_404(Pedido, id=order_id, customer=customer)

        # Verificar si el pedido ya está cancelado o si su estado no permite cancelación
        if pedido.status == "cancelled":
            return Response({"detail": "El pedido ya ha sido cancelado."}, status=status.HTTP_400_BAD_REQUEST)

        if pedido.status == "completed":
            return Response({"detail": "El pedido ya ha sido completado y no puede ser cancelado."}, status=status.HTTP_400_BAD_REQUEST)

        # Cambiar el estado del pedido a "cancelado"
        pedido.status = "cancelled"
        pedido.save()

        # Responder con el pedido actualizado
        response_data = {
            "order_id": pedido.id,
            "customer_id": customer.id,
            "username": customer.user.username,
            "status": pedido.status,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
#http://127.0.0.1:8000/pedidos/deleteOrderUser/id/
class DeleteOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        # Obtener el cliente autenticado
        customer = get_object_or_404(Customer, user=request.user)

        # Obtener el ID del pedido desde la URL o los parámetros de la solicitud
        order_id = kwargs.get("order_id")

        # Obtener el pedido, asegurándose de que pertenezca al cliente autenticado
        pedido = get_object_or_404(Pedido, id=order_id, customer=customer)

        # Verificar si el pedido está en un estado que permita su eliminación
        if pedido.status not in ["cancelled", "delivered"]:
            return Response(
                {"detail": "Primero cancela el pedido o espera que se te entregue."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Borrar el pedido
        pedido.delete()

        # Responder con un mensaje de éxito
        return Response({"detail": "El pedido ha sido eliminado."}, status=status.HTTP_204_NO_CONTENT)