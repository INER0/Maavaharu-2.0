from django.contrib import admin

from .models import Event, ThemeParkTicket


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'date', 'time', 'available_capacity', 'price')
    list_filter = ('event_type', 'date')
    search_fields = ('name', 'description')


@admin.register(ThemeParkTicket)
class ThemeParkTicketAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'event', 'quantity', 'channel', 'purchased_at')
    list_filter = ('channel', 'purchased_at')
    search_fields = ('visitor__username', 'event__name')
