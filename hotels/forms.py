from django import forms
from django.utils import timezone

from .models import Hotel, HotelBooking, HotelPromotion, Room


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(file, initial) for file in data]
        return single_file_clean(data, initial)


class HotelStaffHotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ('name', 'location', 'description')


class HotelStaffRoomForm(forms.ModelForm):
    images = MultipleImageField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'}),
        help_text='You can select more than one room picture.'
    )

    class Meta:
        model = Room
        fields = ('hotel', 'room_type', 'price_per_night', 'total_rooms')
        widgets = {
            'room_type': forms.TextInput(attrs={
                'placeholder': 'Example: Beach Villa, Family Room, Lagoon Suite'
            }),
            'price_per_night': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'total_rooms': forms.NumberInput(attrs={'min': 1}),
        }


class HotelStaffPromotionForm(forms.ModelForm):
    images = MultipleImageField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'}),
        help_text='You can select more than one promotion picture.'
    )

    class Meta:
        model = HotelPromotion
        fields = ('hotel', 'title', 'description', 'discount_percent', 'valid_until')
        widgets = {
            'discount_percent': forms.NumberInput(attrs={
                'min': 1,
                'max': 100,
                'placeholder': 'Leave blank for normal advertisement'
            }),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discount_percent'].required = False
        self.fields['discount_percent'].label = 'Discount percent (optional)'


class HotelBookingStatusForm(forms.ModelForm):
    class Meta:
        model = HotelBooking
        fields = ('status',)

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        booking = self.instance

        if status == HotelBooking.Status.CONFIRMED:
            available_rooms = booking.room.available_rooms(
                booking.check_in,
                booking.check_out,
                exclude_booking=booking,
            )
            if booking.num_rooms > available_rooms:
                self.add_error(
                    'status',
                    f'Only {available_rooms} room(s) are available for these dates.'
                )

        return cleaned_data


class HotelBookingForm(forms.ModelForm):
    class Meta:
        model = HotelBooking
        fields = (
            'room', 'check_in', 'check_out', 'num_rooms',
            'adults', 'kids', 'special_requests',
        )
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
            'num_rooms': forms.NumberInput(attrs={'min': 1}),
            'adults': forms.NumberInput(attrs={'min': 1}),
            'kids': forms.NumberInput(attrs={'min': 0}),
            'special_requests': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Arrival time, room preference, allergies, or anything hotel staff should know.'
            }),
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

        if room and check_in and check_out and check_out > check_in and num_rooms:
            available_rooms = room.available_rooms(check_in, check_out)
            if num_rooms > available_rooms:
                self.add_error(
                    'num_rooms',
                    f'Only {available_rooms} room(s) are available for these dates.'
                )

        return cleaned_data
