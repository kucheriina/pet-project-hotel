from django.db import models


# Create your models here.
class Room(models.Model):
    ECONOMY = 'economy'
    STANDARD = 'standard'
    LUX = 'lux'

    ROOM_CLASS_CHOICES = [
        (ECONOMY, 'Эконом'),
        (STANDARD, 'Стандарт'),
        (LUX, 'Люкс')
    ]

    ONE_BED = '1'
    TWO_BED = '2'
    FAMILY = 'family'

    BED_TYPE_CHOICES = [
        (ONE_BED, 'Одна кровать'),
        (TWO_BED, 'Две кровати'),
        (FAMILY, 'Семейный номер'),
    ]

    room_class = models.CharField(max_length=20, choices=ROOM_CLASS_CHOICES)
    bed_type = models.CharField(max_length=10, choices=BED_TYPE_CHOICES)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f'{self.get_room_class_display()} - {self.price_per_night}₽'
