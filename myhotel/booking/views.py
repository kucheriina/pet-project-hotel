from django.shortcuts import render, get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from catalog.models import Room
from .models import Booking
from .serializers import BookingSerializer


# Create your views here.
class BookingViewSet(ViewSet):
    @swagger_auto_schema(
        operation_description="Создание новой брони",
        request_body=BookingSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response('Бронь создана', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'booking_id': openapi.Schema(type=openapi.TYPE_INTEGER)}
            )),
            status.HTTP_404_NOT_FOUND: openapi.Response('Номер не найден'),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Ошибка валидации')
        }
    )
    @action(detail=False, methods=['post'], url_path='create')
    def create_booking(self, request):
        serializer = BookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        room = serializer.validated_data.get('room')
        date_start = serializer.validated_data.get('date_start')
        date_end = serializer.validated_data.get('date_end')

        get_object_or_404(Room, pk=room.id)

        overlapping_bookings = Booking.objects.filter(
            room=room,
            date_start__lt=date_end,
            date_end__gt=date_start
        )

        if overlapping_bookings.exists():
            return Response(
                {'detail': 'Номер уже забронирован на указанные даты'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking = serializer.save()
        return Response({'booking_id': booking.id}, status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Удаление брони",
        responses={
            status.HTTP_200_OK: openapi.Response('Бронь удалена'),
            status.HTTP_404_NOT_FOUND: openapi.Response('Номер не найден', openapi.Schema(type=openapi.TYPE_OBJECT))
        }
    )
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_booking(self, request, pk=None):
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        return Response({'message': 'Номер удален'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Получения списка всех броней номера отеля по ID номера отеля",
        manual_parameters=[
            openapi.Parameter('room_id', openapi.IN_QUERY, description='ID номера', type=openapi.TYPE_INTEGER)
        ],
        responses={
            status.HTTP_200_OK: BookingSerializer(many=True),
            status.HTTP_400_BAD_REQUEST: openapi.Response('Ошибка запроса', openapi.Schema(type=openapi.TYPE_OBJECT))
        }
    )
    @action(detail=False, methods=['get'], url_path='list')
    def list_bookings(self, request):
        room_id = request.query_params.get('room_id')
        if not room_id:
            return Response({'detail': 'room_id обязателен для заполнения'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            room_id = int(room_id)
        except ValueError:
            return Response({'detail': 'room_id должно быть числом'}, status=status.HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(room_id=room_id)

        data = [
            {
                'booking_id': b.id,
                'date_start': b.date_start.strftime('%Y-%m-%d'),
                'date_end': b.date_end.strftime('%Y-%m-%d')
            }
            for b in bookings
        ]
        return Response(data, status=status.HTTP_200_OK)
