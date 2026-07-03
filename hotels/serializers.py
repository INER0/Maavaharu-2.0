from rest_framework import serializers
from .models import Hotel, Room, HotelBooking, HotelPromotion


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'hotel', 'room_type', 'price_per_night', 'total_rooms']


class HotelSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'description', 'location', 'rooms']


class HotelBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelBooking
        fields = ['id', 'visitor', 'room', 'check_in', 'check_out',
                  'num_rooms', 'status', 'created_at']
        # The visitor is taken from the logged-in user, not the request body.
        read_only_fields = ['visitor', 'status', 'created_at']

    def validate(self, data):
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError('check_out must be after check_in.')
        return data


class HotelPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelPromotion
        fields = ['id', 'hotel', 'title', 'description', 'discount_percent', 'valid_until']
