from django.contrib import admin

from .models import (
    Event, EventImage, SpecialThemeParkEvent, ThemeParkEntranceTicket, ThemeParkPromotion, ThemeParkTicket,
    WeeklyThemeParkEvent,
)


class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'schedule_type', 'weekday', 'date', 'time', 'available_capacity', 'price')
    list_filter = ('event_type', 'schedule_type', 'weekday', 'date')
    search_fields = ('name', 'description')
    inlines = [EventImageInline]


@admin.register(WeeklyThemeParkEvent)
class WeeklyThemeParkEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'weekdays', 'time', 'available_capacity', 'price')
    list_filter = ('event_type',)
    search_fields = ('name', 'description')
    fields = ('name', 'event_type', 'weekdays', 'description', 'time', 'capacity', 'available_capacity', 'price')
    inlines = [EventImageInline]


@admin.register(SpecialThemeParkEvent)
class SpecialThemeParkEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'date', 'time', 'available_capacity', 'price')
    list_filter = ('event_type', 'date')
    search_fields = ('name', 'description')
    fields = ('name', 'event_type', 'description', 'date', 'time', 'capacity', 'available_capacity', 'price')
    inlines = [EventImageInline]


@admin.register(ThemeParkTicket)
class ThemeParkTicketAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'event', 'quantity', 'channel', 'purchased_at')
    list_filter = ('channel', 'purchased_at')
    search_fields = ('visitor__username', 'event__name')


@admin.register(ThemeParkEntranceTicket)
class ThemeParkEntranceTicketAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'visit_date', 'quantity', 'price_per_ticket', 'channel', 'purchased_at')
    list_filter = ('channel', 'visit_date', 'purchased_at')
    search_fields = ('visitor__username',)


@admin.register(ThemeParkPromotion)
class ThemeParkPromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'discount_percent', 'valid_until')
    list_filter = ('valid_until', 'event__event_type')
    search_fields = ('title', 'description', 'event__name')
