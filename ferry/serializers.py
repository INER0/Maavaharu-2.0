from rest_framework import serializers
from .models import FerrySchedule


class FerryScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FerrySchedule
        fields = ['id', 'origin', 'destination', 'date', 'departure_time',
                  'capacity', 'available_seats', 'price']
