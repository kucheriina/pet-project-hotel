from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .serializers import RoomSerializer
from .models import Room


# Create your views here.
class RoomViewSet(ViewSet):
    @swagger_auto_schema(
        operation_description="Создание нового номера",
        request_body=RoomSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Номер создан', RoomSerializer),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Ошибка создания', openapi.Schema(type=openapi.TYPE_OBJECT))
        }
    )
    @action(detail=False, methods=['post'], url_path='create')
    def create_room(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            return Response({'room_id': room.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление номера по ID",
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response('Номер удален'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Номер не найден', openapi.Schema(type=openapi.TYPE_OBJECT))
        }
    )
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_room(self, request, pk=None):
        room = get_object_or_404(Room, pk=pk)
        room.delete()
        return Response({'message': 'Номер удален'}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Получить список всех номеров",
        manual_parameters=[
            openapi.Parameter('sort_by', openapi.IN_QUERY, description="Поле для сортировки (price_per_night, "
                                                                       "created_at)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('order', openapi.IN_QUERY, description="Порядок сортировки (asc, desc)",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            200: RoomSerializer(many=True),
            status.HTTP_404_NOT_FOUND: openapi.Response('Номера не найдены', openapi.Schema(type=openapi.TYPE_OBJECT))
        }
    )
    @action(detail=False, methods=['get'], url_path='list')
    def list_room(self, request):
        sort_by = request.query_params.get('sort_by', 'price_per_night')
        order = request.query_params.get('order', 'asc')

        if sort_by not in ['price_per_night', 'created_at']:
            return Response({'detail': 'Неверные параметры сортировки'},  status.HTTP_400_BAD_REQUEST)

        if order not in ['asc', 'desc']:
            return Response({'detail': 'Неверный параметр порядка сортировки'}, status.HTTP_400_BAD_REQUEST)

        if order == 'asc':
            rooms = Room.objects.all().order_by(sort_by)
        else:
            rooms = Room.objects.all().order_by(F(sort_by).desc())

        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
