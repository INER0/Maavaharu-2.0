from rest_framework import serializers
from .models import Hotel, Room, RoomImage, HotelBooking, HotelPromotion, HotelPromotionImage


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['id', 'image', 'caption']


class HotelPromotionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelPromotionImage
        fields = ['id', 'image', 'caption']


class RoomSerializer(serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'hotel', 'room_type', 'price_per_night', 'total_rooms', 'images']


class HotelSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'description', 'location', 'rooms']


class HotelBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelBooking
        fields = ['id', 'visitor', 'room', 'check_in', 'check_out',
                  'num_rooms', 'adults', 'kids', 'special_requests',
                  'status', 'created_at']
        # The visitor is taken from the logged-in user, not the request body.
        read_only_fields = ['visitor', 'status', 'created_at']

    def validate(self, data):
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError('check_out must be after check_in.')
        return data


class HotelPromotionSerializer(serializers.ModelSerializer):
    images = HotelPromotionImageSerializer(many=True, read_only=True)

    class Meta:
        model = HotelPromotion
        fields = ['id', 'hotel', 'title', 'description', 'discount_percent', 'valid_until', 'images']
