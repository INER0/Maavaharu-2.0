import uuid

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    """A custom room type in Maavaharu Hotel, with how many exist."""
    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    room_type = models.CharField(max_length=100)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_type}"

    def occupied_rooms(self, check_in, check_out, exclude_booking=None):
        bookings = self.bookings.filter(
            status__in=[HotelBooking.Status.PENDING, HotelBooking.Status.CONFIRMED],
            check_in__lt=check_out,
            check_out__gt=check_in,
        )
        if exclude_booking:
            bookings = bookings.exclude(id=exclude_booking.id)
        return bookings.aggregate(total=Sum('num_rooms'))['total'] or 0

    def available_rooms(self, check_in, check_out, exclude_booking=None):
        return max(self.total_rooms - self.occupied_rooms(check_in, check_out, exclude_booking), 0)


class RoomImage(models.Model):
    room = models.ForeignKey(Room, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hotel_rooms/')
    caption = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.room}"


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
    adults = models.PositiveIntegerField(default=1)
    kids = models.PositiveIntegerField(default=0)
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    verification_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
    discount_percent = models.PositiveIntegerField(blank=True, null=True)
    valid_until = models.DateField()

    def __str__(self):
        return self.title


class HotelPromotionImage(models.Model):
    promotion = models.ForeignKey(HotelPromotion, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hotel_promotions/')
    caption = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.promotion.title}"
