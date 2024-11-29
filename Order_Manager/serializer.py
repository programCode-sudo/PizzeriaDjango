from rest_framework import serializers
from Pedidos.models import Pedido,PedidoFoodItem
from RestauranteData.Food_Item import FoodItem
from Order_Manager.models import Order_Manager

class PedidoFoodItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()  # ID del FoodItem
    quantity = serializers.IntegerField(min_value=1)  # Cantidad

class PedidoSerializer(serializers.ModelSerializer):
    food_items = PedidoFoodItemSerializer(many=True)
    order_manager_id = serializers.IntegerField(required=True)
    caller_name = serializers.CharField(max_length=255)
    caller_address = serializers.CharField(max_length=255)
    caller_phone = serializers.CharField(max_length=15)

    class Meta:
        model = Pedido
        fields = ['description', 'caller_name', 'caller_address', 'caller_phone', 'order_manager_id', 'food_items']

    def validate_order_manager_id(self, value):
        try:
            Order_Manager.objects.get(id=value)
        except Order_Manager.DoesNotExist:
            raise serializers.ValidationError("Order Manager no encontrado.")
        return value

    def validate_food_items(self, value):
        for item in value:
            try:
                food_item = FoodItem.objects.get(id=item['id'])
                if food_item.stockRestaurant < item['quantity']:
                    raise serializers.ValidationError(
                        f"Stock insuficiente para {food_item.name}. Disponible: {food_item.stockRestaurant}"
                    )
            except FoodItem.DoesNotExist:
                raise serializers.ValidationError(f"FoodItem con ID {item['id']} no encontrado.")
        return value

    def create(self, validated_data):
        # Obtener Order Manager
        order_manager = Order_Manager.objects.get(id=validated_data['order_manager_id'])

        # Crear el pedido
        pedido = Pedido.objects.create(
            description=validated_data.get('description', 'Pedido por llamada'),
            address=validated_data['caller_address'],
            status="En_Espera",
            order_manager=order_manager,
            caller_name=validated_data['caller_name'],
            caller_phone=validated_data['caller_phone'],
        )

        # Asociar food_items
        food_items = validated_data['food_items']
        for item in food_items:
            food_item = FoodItem.objects.get(id=item['id'])
            PedidoFoodItem.objects.create(pedido=pedido, food_item=food_item, quantity=item['quantity'])

            # Reducir el stock
            food_item.stockRestaurant -= item['quantity']
            food_item.save()

        return pedido
