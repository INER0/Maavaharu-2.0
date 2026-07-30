from rest_framework import serializers
from .models import FerrySchedule


class FerryScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FerrySchedule
        fields = [
            'id', 'route_name', 'origin', 'destination', 'schedule_type',
            'weekdays', 'date', 'departure_time', 'return_time',
            'capacity', 'available_seats', 'price',
        ]
