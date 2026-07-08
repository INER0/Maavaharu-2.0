from django import forms
from django.utils import timezone

from .models import HotelBooking, Room


class HotelBookingForm(forms.ModelForm):
    class Meta:
        model = HotelBooking
        fields = ('room', 'check_in', 'check_out', 'num_rooms')
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
            'num_rooms': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.select_related('hotel').all()
        self.fields['room'].empty_label = 'Choose a room type'

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        num_rooms = cleaned_data.get('num_rooms')
        room = cleaned_data.get('room')

        if check_in and check_in < timezone.now().date():
            self.add_error('check_in', 'Check-in date cannot be in the past.')

        if check_in and check_out and check_out <= check_in:
            self.add_error('check_out', 'Check-out date must be after check-in date.')

        if room and num_rooms and num_rooms > room.total_rooms:
            self.add_error('num_rooms', 'Requested rooms exceed the available room count.')

        return cleaned_data
