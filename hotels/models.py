from django.conf import settings
from django.db import models
from django.utils import timezone


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    """A type of room in a hotel (e.g. 'Deluxe'), with how many exist."""
    class RoomType(models.TextChoices):
        STANDARD = 'standard', 'Standard'
        DELUXE = 'deluxe', 'Deluxe'
        SUITE = 'suite', 'Suite'

    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    room_type = models.CharField(max_length=20, choices=RoomType.choices)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.hotel.name} - {self.get_room_type_display()}"


class HotelBooking(models.Model):
    """A visitor's reservation of a room for a date range."""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    visitor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='hotel_bookings', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, related_name='bookings', on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    num_rooms = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.visitor} @ {self.room} ({self.status})"

    @property
    def is_valid(self):
        """A booking is 'valid' for ferry purposes if it is confirmed and has
        not already ended."""
        return self.status == self.Status.CONFIRMED and self.check_out >= timezone.now().date()


class HotelPromotion(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='promotions', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    discount_percent = models.PositiveIntegerField(default=0)
    valid_until = models.DateField()

    def __str__(self):
        return self.title
