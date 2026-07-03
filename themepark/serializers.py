from rest_framework import serializers
from .models import Event, ThemeParkTicket


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'event_type', 'description', 'date', 'time',
                  'capacity', 'available_capacity', 'price']


class ThemeParkTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThemeParkTicket
        fields = ['id', 'visitor', 'event', 'quantity', 'channel', 'purchased_at']
        read_only_fields = ['visitor', 'purchased_at']

    def validate(self, data):
        if data['quantity'] > data['event'].available_capacity:
            raise serializers.ValidationError('Not enough capacity left for this event.')
        return data
