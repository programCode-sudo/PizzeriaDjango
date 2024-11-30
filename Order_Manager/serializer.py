from rest_framework import serializers
from Pedidos.models import Pedido, PedidoFoodItem
from RestauranteData.models import FoodItem

class PedidoSerializer(serializers.ModelSerializer):
    food_items = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),  # Lista de objetos con ID y quantity
        write_only=True  # No se incluirá en la representación de la respuesta
    )
    
    class Meta:
        model = Pedido
        fields = ['customer_name', 'customer_email', 'customer_phone', 'address', 'description', 'food_items']
    
    def create(self, validated_data):
        food_items_data = validated_data.pop('food_items')
        
        # Validar que todos los food_item_id existan
        food_item_ids = [item['food_item_id'] for item in food_items_data]
        existing_food_items = FoodItem.objects.filter(id__in=food_item_ids)
        if existing_food_items.count() != len(food_item_ids):
            raise serializers.ValidationError("Uno o más food_item_id no son válidos. Verifica los datos enviados.")
        
        # Configurar estado automáticamente en "Pendiente"
        validated_data['status'] = 'Pendiente'
        
        # Crear el pedido
        pedido = Pedido.objects.create(**validated_data)
        
        # Crear los food_items asociados al pedido y reducir el stock
        total_price = 0
        for item_data in food_items_data:
            food_item = existing_food_items.get(id=item_data['food_item_id'])
            quantity = item_data['quantity']
            
            # Verificar que hay suficiente stock
            if food_item.stockRestaurant < quantity:
                raise serializers.ValidationError(f"No hay suficiente stock para el artículo {food_item.name}.")
            
            # Reducir el stock
            food_item.stockRestaurant -= quantity
            food_item.save()
            
            # Calcular el precio total
            total_price += food_item.unitPrice * quantity
            
            PedidoFoodItem.objects.create(
                pedido=pedido,
                food_item_name=food_item.name,
                food_item_price=food_item.unitPrice,
                quantity=quantity,
                food_item_description=food_item.description,
                food_item_image=food_item.image
            )
        
        # Actualizar el total del pedido
        pedido.Total = total_price
        pedido.save()
        
        return pedido

class PedidoFoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoFoodItem
        fields = ['food_item_name', 'food_item_price', 'quantity', 'food_item_description', 'food_item_image']

class PedidoSerializerPersonalizado(serializers.ModelSerializer):
    food_items = PedidoFoodItemSerializer(source='pedidofooditem_set', many=True)
    
    class Meta:
        model = Pedido
        fields = ['id', 'created_at', 'description', 'address', 'status', 
                  'customer_name', 'customer_email', 'customer_phone', 
                  'order_manager', 'order_dispatcher', 'delivery_person', 
                  'Total', 'food_items']

    def to_representation(self, instance):
        # Convertir el pedido en una representación JSON
        data = super().to_representation(instance)
        
        # Si el pedido tiene un cliente relacionado, usamos los datos del cliente
        if instance.customer:
            customer = instance.customer
            data['customer_name'] = customer.user.username
            data['customer_email'] = customer.user.email
            data['customer_phone'] = customer.phone
        
        return data
