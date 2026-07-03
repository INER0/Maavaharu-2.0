from django.conf import settings
from django.db import models


class Event(models.Model):
    """A bookable thing inside the park: a ride, a show, or a beach event."""
    class EventType(models.TextChoices):
        RIDE = 'ride', 'Ride'
        SHOW = 'show', 'Show'
        BEACH = 'beach_event', 'Beach Event'

    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    capacity = models.PositiveIntegerField(default=100)
    available_capacity = models.PositiveIntegerField(default=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()}) on {self.date}"


class ThemeParkTicket(models.Model):
    """A purchase of one or more spots for an event."""
    class Channel(models.TextChoices):
        ONLINE = 'online', 'Online'
        ENTRANCE = 'entrance', 'At Entrance'

    visitor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='themepark_tickets',
                                on_delete=models.CASCADE, null=True, blank=True)
    event = models.ForeignKey(Event, related_name='tickets', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    channel = models.CharField(max_length=20, choices=Channel.choices, default=Channel.ONLINE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.event.name}"
