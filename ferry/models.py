from django.db import models


class FerrySchedule(models.Model):
    """A single ferry trip on a given date/time, with seat capacity."""
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    date = models.DateField()
    departure_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=50)
    available_seats = models.PositiveIntegerField(default=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.origin} -> {self.destination} on {self.date}"
