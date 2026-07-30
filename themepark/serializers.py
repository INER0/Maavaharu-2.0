from rest_framework import serializers
from .models import Event, EventImage, ThemeParkEntranceTicket, ThemeParkPromotion, ThemeParkTicket


class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image', 'caption']


class EventSerializer(serializers.ModelSerializer):
    images = EventImageSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'event_type', 'schedule_type', 'weekday', 'weekdays',
            'description', 'date', 'time', 'capacity', 'available_capacity', 'price',
            'images',
        ]


class ThemeParkTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeParkTicket
        fields = ['id', 'visitor', 'event', 'quantity', 'channel', 'verification_code', 'purchased_at']
        read_only_fields = ['visitor', 'verification_code', 'purchased_at']

    def validate(self, data):
        available_capacity = data['event'].available_capacity
        if available_capacity is not None and data['quantity'] > available_capacity:
            raise serializers.ValidationError('Not enough capacity left for this event.')
        return data


class ThemeParkPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeParkPromotion
        fields = ['id', 'event', 'title', 'description', 'discount_percent', 'valid_until']


class ThemeParkEntranceTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeParkEntranceTicket
        fields = [
            'id', 'visitor', 'visit_date', 'quantity', 'price_per_ticket',
            'channel', 'verification_code', 'purchased_at',
        ]
        read_only_fields = ['visitor', 'verification_code', 'purchased_at']
