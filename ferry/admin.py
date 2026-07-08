from django.contrib import admin

from .models import FerrySchedule


@admin.register(FerrySchedule)
class FerryScheduleAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'date', 'departure_time', 'available_seats', 'price')
    list_filter = ('date', 'origin', 'destination')
    search_fields = ('origin', 'destination')
