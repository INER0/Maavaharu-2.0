from django.contrib import admin

from .models import FerrySchedule, FerryTicket


@admin.register(FerrySchedule)
class FerryScheduleAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'date', 'departure_time', 'available_seats', 'price')
    list_filter = ('date', 'origin', 'destination')
    search_fields = ('origin', 'destination')


@admin.register(FerryTicket)
class FerryTicketAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'schedule', 'hotel_booking', 'seats', 'status', 'issued_at')
    list_filter = ('status', 'issued_at')
    search_fields = ('visitor__username', 'schedule__origin', 'schedule__destination')
