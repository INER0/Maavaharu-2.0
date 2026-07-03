from rest_framework import serializers
from hotels.models import HotelBooking
from .models import FerrySchedule, FerryTicket


class FerryScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FerrySchedule
        fields = ['id', 'origin', 'destination', 'date', 'departure_time',
                  'capacity', 'available_seats', 'price']


class FerryTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = FerryTicket
        fields = ['id', 'visitor', 'schedule', 'hotel_booking', 'seats',
                  'status', 'issued_at']
        read_only_fields = ['visitor', 'status', 'issued_at']

    def validate(self, data):
        """This is where the core rule lives: a ferry ticket is only allowed
        if the requesting visitor owns a VALID hotel booking."""
        request = self.context['request']
        visitor = request.user

        # 1. Does the visitor have ANY valid hotel booking?
        valid_bookings = [b for b in HotelBooking.objects.filter(visitor=visitor)
                          if b.is_valid]
        if not valid_bookings:
            raise serializers.ValidationError(
                'You must have a valid (confirmed) hotel booking to buy a ferry ticket.'
            )

        # 2. The hotel_booking they pointed at must be their own and valid.
        booking = data['hotel_booking']
        if booking.visitor != visitor or not booking.is_valid:
            raise serializers.ValidationError(
                'The selected hotel booking is not a valid booking of yours.'
            )

        # 3. Enough seats left on the ferry?
        if data['seats'] > data['schedule'].available_seats:
            raise serializers.ValidationError('Not enough seats available on this ferry.')

        return data
