from django.contrib import admin

from .models import Advertisement, MapLocation


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')


@admin.register(MapLocation)
class MapLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'latitude', 'longitude')
    list_filter = ('category',)
    search_fields = ('name', 'category', 'description')
