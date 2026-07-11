from django.contrib import admin

from .models import Hotel, HotelBooking, HotelPromotion, HotelPromotionImage, Room, RoomImage


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1


class HotelPromotionImageInline(admin.TabularInline):
    model = HotelPromotionImage
    extra = 1


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location', 'description')
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'room_type', 'price_per_night', 'total_rooms')
    list_filter = ('room_type', 'hotel')
    search_fields = ('hotel__name', 'room_type')
    inlines = [RoomImageInline]


@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'room', 'check_in', 'check_out', 'num_rooms', 'status')
    list_filter = ('status', 'check_in', 'check_out')
    search_fields = ('visitor__username', 'room__hotel__name')


@admin.register(HotelPromotion)
class HotelPromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'hotel', 'discount_percent', 'valid_until')
    list_filter = ('hotel', 'valid_until')
    search_fields = ('title', 'description', 'hotel__name')
    inlines = [HotelPromotionImageInline]
