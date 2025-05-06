from django.db import models
from catalog.models import Room


# Create your models here.
class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    date_start = models.DateField()
    date_end = models.DateField()

    def __str__(self):
        return f'Бронь #{self.id} для номера {self.room} с {self.date_start} по {self.date_end}'