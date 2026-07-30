import uuid

from django.conf import settings
from django.db import models


class Event(models.Model):
    """A bookable thing inside the park: an activity, a show, or a beach event."""
    class EventType(models.TextChoices):
        ACTIVITY = 'activity', 'Activity'
        SHOW = 'show', 'Show'
        BEACH = 'beach_event', 'Beach Event'

    class ScheduleType(models.TextChoices):
        WEEKLY = 'weekly', 'Weekly Schedule'
        SPECIAL = 'special', 'Special Dated Event'

    class Weekday(models.TextChoices):
        MONDAY = 'monday', 'Monday'
        TUESDAY = 'tuesday', 'Tuesday'
        WEDNESDAY = 'wednesday', 'Wednesday'
        THURSDAY = 'thursday', 'Thursday'
        FRIDAY = 'friday', 'Friday'
        SATURDAY = 'saturday', 'Saturday'
        SUNDAY = 'sunday', 'Sunday'

    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    schedule_type = models.CharField(max_length=20, choices=ScheduleType.choices, default=ScheduleType.WEEKLY)
    weekday = models.CharField(max_length=20, choices=Weekday.choices, blank=True)
    weekdays = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    available_capacity = models.PositiveIntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()}) - {self.schedule_label}"

    @property
    def schedule_label(self):
        time_label = f" at {self.time}" if self.time else ''
        if self.schedule_type == self.ScheduleType.SPECIAL:
            if self.date:
                return f"{self.date}{time_label}"
            return f"Special event{time_label}"
        if self.weekdays:
            labels = dict(self.Weekday.choices)
            weekday_values = {choice[0] for choice in self.Weekday.choices}
            selected_values = set(self.weekdays)
            if selected_values == weekday_values:
                return f"Every day{time_label}"
            days = ', '.join(labels.get(day, day.title()) for day in self.weekdays)
            return f"Every {days}{time_label}"
        if self.weekday:
            return f"Every {self.get_weekday_display()}{time_label}"
        return f"Weekly schedule{time_label}"


class WeeklyEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(schedule_type=Event.ScheduleType.WEEKLY)


class SpecialEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(schedule_type=Event.ScheduleType.SPECIAL)


class WeeklyThemeParkEvent(Event):
    objects = WeeklyEventManager()

    class Meta:
        proxy = True
        verbose_name = 'Weekly Theme Park Activity'
        verbose_name_plural = 'Weekly Theme Park Activities'

    def save(self, *args, **kwargs):
        self.schedule_type = Event.ScheduleType.WEEKLY
        self.date = None
        if self.weekdays:
            self.weekday = self.weekdays[0]
        super().save(*args, **kwargs)


class SpecialThemeParkEvent(Event):
    objects = SpecialEventManager()

    class Meta:
        proxy = True
        verbose_name = 'Special Theme Park Event'
        verbose_name_plural = 'Special Theme Park Events'

    def save(self, *args, **kwargs):
        self.schedule_type = Event.ScheduleType.SPECIAL
        self.weekday = ''
        self.weekdays = []
        super().save(*args, **kwargs)


class EventImage(models.Model):
    event = models.ForeignKey(Event, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='themepark_events/')
    caption = models.CharField(max_length=150, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.event.name}"


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
    verification_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.event.name}"


class ThemeParkEntranceTicket(models.Model):
    """General theme park entry ticket, separate from activity/event bookings."""
    class Channel(models.TextChoices):
        ONLINE = 'online', 'Online'
        ENTRANCE = 'entrance', 'At Entrance'

    visitor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='themepark_entrance_tickets',
                                on_delete=models.CASCADE, null=True, blank=True)
    visit_date = models.DateField()
    quantity = models.PositiveIntegerField(default=1)
    price_per_ticket = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    channel = models.CharField(max_length=20, choices=Channel.choices, default=Channel.ENTRANCE)
    verification_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    purchased_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.quantity * self.price_per_ticket

    def __str__(self):
        return f"{self.quantity} entrance ticket(s) for {self.visit_date}"


class ThemeParkPromotion(models.Model):
    event = models.ForeignKey(Event, related_name='promotions', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    discount_percent = models.PositiveIntegerField(blank=True, null=True)
    valid_until = models.DateField()

    def __str__(self):
        return self.title
