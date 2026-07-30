from django.db import models


class FerrySchedule(models.Model):
    """A recurring or dated ferry route with seat capacity."""
    class ScheduleType(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        SPECIAL = 'special', 'Special Date'

    class Weekday(models.TextChoices):
        MONDAY = 'monday', 'Monday'
        TUESDAY = 'tuesday', 'Tuesday'
        WEDNESDAY = 'wednesday', 'Wednesday'
        THURSDAY = 'thursday', 'Thursday'
        FRIDAY = 'friday', 'Friday'
        SATURDAY = 'saturday', 'Saturday'
        SUNDAY = 'sunday', 'Sunday'

    route_name = models.CharField(max_length=150, blank=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    schedule_type = models.CharField(max_length=20, choices=ScheduleType.choices, default=ScheduleType.DAILY)
    weekdays = models.JSONField(default=list, blank=True)
    date = models.DateField(blank=True, null=True)
    departure_time = models.TimeField()
    return_time = models.TimeField(blank=True, null=True)
    capacity = models.PositiveIntegerField(default=50)
    available_seats = models.PositiveIntegerField(default=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.route_label} - {self.schedule_label}"

    @property
    def route_label(self):
        if self.route_name:
            return self.route_name
        return f"{self.origin} to {self.destination}"

    @property
    def schedule_label(self):
        if self.schedule_type == self.ScheduleType.DAILY:
            return 'Every day'
        if self.schedule_type == self.ScheduleType.SPECIAL:
            return str(self.date) if self.date else 'Special date'
        if self.weekdays:
            labels = dict(self.Weekday.choices)
            weekday_values = {choice[0] for choice in self.Weekday.choices}
            selected_values = set(self.weekdays)
            if selected_values == weekday_values:
                return 'Every day'
            return 'Every ' + ', '.join(labels.get(day, day.title()) for day in self.weekdays)
        return 'Weekly schedule'
