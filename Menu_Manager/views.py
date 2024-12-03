# Menu_Manager/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from RestauranteData.Food_Item import FoodItem
from RestauranteData.models import Restaurante
from .serializer import FoodItemSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AddFoodItemToRestaurantView(APIView):

    @swagger_auto_schema(
        operation_description="Agregar un item de comida al restaurante con id 1.",
        request_body=FoodItemSerializer,
        responses={
            201: openapi.Response(description="Item de comida agregado correctamente", examples={'application/json': {"message": "Food item agregado al restaurante exitosamente", "food_item_id": 1}}),
            400: "Bad Request",
            404: "Restaurante no encontrado"
        }
    )

    def post(self, request):
        serializer = FoodItemSerializer(data=request.data)
        if serializer.is_valid():
            # Guardar el FoodItem
            food_item = serializer.save()
            
            try:
                # Asociar el FoodItem al restaurante con id 1
                restaurante = Restaurante.objects.get(id=1)
                restaurante.food_item.add(food_item)
                return Response({
                    "message": "Food item agregado al restaurante exitosamente",
                    "food_item_id": food_item.id
                }, status=status.HTTP_201_CREATED)
            except Restaurante.DoesNotExist:
                food_item.delete()  # Eliminar el FoodItem si no se puede asociar
                return Response({"error": "Restaurante no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllFoodItemsView(APIView):

    @swagger_auto_schema(
        operation_description="Obtener todos los items de comida.",
        responses={
            200: FoodItemSerializer(many=True),
        }
    )

    def get(self,request):
        food_items = FoodItem.objects.all()

        serializer = FoodItemSerializer(food_items,many=True)
        for item in  serializer.data:
            item['image_url'] = request.build_absolute_uri(item['image'])
        return Response(serializer.data,status=status.HTTP_200_OK)

class GetActiveFoodItemsView(APIView):
    @swagger_auto_schema(
        operation_description="Obtener los items de comida activos.",
        responses={
            200: FoodItemSerializer(many=True),
        }
    )
    def get(self, request):
        food_items = FoodItem.objects.filter(isActive=True)
        serializer = FoodItemSerializer(food_items, many=True)
        for item in serializer.data:
            item['image_url'] = request.build_absolute_uri(item['image'])
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteFoodItemView(APIView):

    @swagger_auto_schema(
        operation_description="Eliminar un item de comida por su id.",
        responses={
            204: "No Content",
            404: "Food item no encontrado",
        }
    )

    def delete(self, request, food_item_id):
        try:
            food_item = FoodItem.objects.get(id=food_item_id)
            food_item.delete()
            return Response({"message": "Food item eliminado exitosamente"}, status=status.HTTP_204_NO_CONTENT)
        except FoodItem.DoesNotExist:
            return Response({"error": "Food item no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
class GetOneFoodItemView(APIView):

    @swagger_auto_schema(
        operation_description="Obtener un item de comida por su nombre y categoría.",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="Nombre del item de comida", type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, description="Categoría del item de comida", type=openapi.TYPE_STRING),
        ],
        responses={
            200: FoodItemSerializer,
            400: "Bad Request",
            404: "Food item no encontrado"
        }
    )

    def get(self, request):
        name = request.query_params.get('name')
        category = request.query_params.get('category')
        
        if not name or not category:
            return Response({"error": "Se requiere nombre y categoría"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            food_item = FoodItem.objects.get(name=name, category=category)
            serializer = FoodItemSerializer(food_item)
            food_item_data = serializer.data
            food_item_data['image_url'] = request.build_absolute_uri(food_item_data['image'])
            return Response(food_item_data, status=status.HTTP_200_OK)
        except FoodItem.DoesNotExist:
            return Response({"error": "Food item no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
class EditFoodItemView(APIView):

    @swagger_auto_schema(
        operation_description="Actualizar los detalles de un item de comida por su id.",
        request_body=FoodItemSerializer,
        responses={
            200: openapi.Response(description="Food item actualizado exitosamente", examples={'application/json': {"message": "Food item actualizado exitosamente", "food_item_id": 1}}),
            404: "Food item no encontrado",
            400: "Bad Request"
        }
    )

    def put(self, request, food_item_id):
        try:
            food_item = FoodItem.objects.get(id=food_item_id)
        except FoodItem.DoesNotExist:
            return Response({"error": "Food item no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos del FoodItem
        serializer = FoodItemSerializer(food_item, data=request.data, partial=True)  # partial=True permite actualizaciones parciales
        if serializer.is_valid():
            updated_food_item = serializer.save()
            return Response({"message": "Food item actualizado exitosamente", "food_item_id": updated_food_item.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetOneFoodItemByIdView(APIView):

    @swagger_auto_schema(
        operation_description="Obtener un item de comida por su id.",
        responses={
            200: FoodItemSerializer,
            404: "Food item no encontrado"
        }
    )

    def get(self, request, food_item_id):
        try:
            food_item = FoodItem.objects.get(id=food_item_id)
            serializer = FoodItemSerializer(food_item)
            food_item_data = serializer.data
            food_item_data['image_url'] = request.build_absolute_uri(food_item_data['image'])
            return Response(food_item_data, status=status.HTTP_200_OK)
        except FoodItem.DoesNotExist:
            return Response({"error": "Food item no encontrado"}, status=status.HTTP_404_NOT_FOUND)

class ChangeFoodItemStatusView(APIView):

    @swagger_auto_schema(
        operation_description="Cambiar el estado de un item de comida.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'isActive': openapi.Schema(type=openapi.TYPE_BOOLEAN)
            }
        ),
        responses={
            200: openapi.Response(description="Estado actualizado exitosamente"),
            404: "Food item no encontrado",
            400: "Bad Request"
        }
    )

    def post(self, request, fooditem_id):
        try:
            food_item = FoodItem.objects.get(id=fooditem_id)
            new_status = request.data.get('isActive', None)
            if new_status is None:
                return Response({'message': 'Debe proporcionar el estado isActive (True o False).'}, status=status.HTTP_400_BAD_REQUEST)
            if not isinstance(new_status, bool):
                return Response({'message': 'El estado isActive debe ser True o False.'}, status=status.HTTP_400_BAD_REQUEST)

            food_item.isActive = new_status
            food_item.save()

            return Response({'message': f'El estado del FoodItem con id {fooditem_id} ha sido actualizado a {new_status} con éxito.'}, status=status.HTTP_200_OK)
        except FoodItem.DoesNotExist:
            return Response({'message': 'El FoodItem no existe.'}, status=status.HTTP_404_NOT_FOUND)



