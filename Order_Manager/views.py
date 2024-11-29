from .serializer import PedidoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class CreateOrderManagerPedidoView(APIView):
    def post(self, request):
        serializer = PedidoSerializer(data=request.data)
        if serializer.is_valid():
            pedido = serializer.save()
            return Response({
                "message": "Pedido creado exitosamente",
                "pedido_id": pedido.id,
                "caller_name": pedido.caller_name,
                "caller_phone": pedido.caller_phone
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)