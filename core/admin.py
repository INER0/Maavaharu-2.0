from django.contrib import admin

from .models import Advertisement, MapImage, MapLocation, SystemIssue


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content')


@admin.register(MapLocation)
class MapLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'latitude', 'longitude', 'pin_x', 'pin_y')
    list_filter = ('category',)
    search_fields = ('name', 'category', 'description')


@admin.register(MapImage)
class MapImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'uploaded_at')
    list_filter = ('is_active', 'uploaded_at')
    search_fields = ('title',)


@admin.register(SystemIssue)
class SystemIssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'resolved_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')
