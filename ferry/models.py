from django.conf import settings
from django.db import models


class FerrySchedule(models.Model):
    """A single ferry trip on a given date/time, with seat capacity."""
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    date = models.DateField()
    departure_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=50)
    available_seats = models.PositiveIntegerField(default=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.origin} -> {self.destination} on {self.date}"


class FerryTicket(models.Model):
    """A ferry pass issued to a visitor. Can ONLY be created when the visitor
    has a valid (confirmed, not-expired) hotel booking."""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ISSUED = 'issued', 'Issued'
        CANCELLED = 'cancelled', 'Cancelled'

    visitor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='ferry_tickets', on_delete=models.CASCADE)
    schedule = models.ForeignKey(FerrySchedule,
                                 related_name='tickets', on_delete=models.CASCADE)
    # The hotel booking that justified this ticket (the business rule).
    hotel_booking = models.ForeignKey('hotels.HotelBooking',
                                      on_delete=models.PROTECT)
    seats = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ferry pass for {self.visitor} ({self.status})"
