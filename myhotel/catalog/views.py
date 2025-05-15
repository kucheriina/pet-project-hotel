from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.pagination import PageNumberPagination
from .serializers import RoomSerializer
from .models import Room


# Create your views here.
class RoomViewSet(ViewSet):
    def get_sorted_queryset(self, request):
        """
        Возвращает queryset номеров с примененной сортировкой на основе query-параметров.
        """
        sort_by = request.query_params.get('sort_by', 'price_per_night').lower()
        order = request.query_params.get('order', 'asc').lower()

        if sort_by not in ['price_per_night', 'created_at']:
            raise ValidationError({'detail': 'Неверный параметр сортировки'})

        if order not in ['asc', 'desc']:
            raise ValidationError({'detail': 'Неверный параметр порядка сортировки'})

        ordering = sort_by if order == 'asc' else F(sort_by).desc()
        return Room.objects.all().order_by(ordering)

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
            status.HTTP_200_OK: openapi.Response('Номер удален'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Номер не найден', openapi.Schema(type=openapi.TYPE_OBJECT))
        }
    )
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_room(self, request, pk=None):
        room = get_object_or_404(Room, pk=pk)
        room.delete()
        return Response({'message': 'Номер удален'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Получить список всех номеров",
        manual_parameters=[
            openapi.Parameter('sort_by', openapi.IN_QUERY, description="Поле для сортировки (price_per_night, "
                                                                       "created_at)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('order', openapi.IN_QUERY, description="Порядок сортировки (asc, desc)",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Номер страницы", type=openapi.TYPE_INTEGER)
        ],
        responses={
            status.HTTP_200_OK: RoomSerializer(many=True),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Ошибка сортировки', openapi.Schema(type=openapi.TYPE_OBJECT))
        }
    )
    @action(detail=False, methods=['get'], url_path='list')
    def list_room(self, request):
        try:
            rooms = self.get_sorted_queryset(request)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        paginator = PageNumberPagination()
        paginated_qs = paginator.paginate_queryset(rooms, request, view=self)
        serializer = RoomSerializer(paginated_qs if paginated_qs is not None else rooms, many=True)

        return paginator.get_paginated_response(serializer.data)


