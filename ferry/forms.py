from django import forms

from .models import FerrySchedule


class FerryScheduleForm(forms.ModelForm):
    class Meta:
        model = FerrySchedule
        fields = ('origin', 'destination', 'date', 'departure_time', 'capacity', 'available_seats')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
            'capacity': forms.NumberInput(attrs={'min': 1}),
            'available_seats': forms.NumberInput(attrs={'min': 0}),
        }

    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get('capacity')
        available_seats = cleaned_data.get('available_seats')

        if capacity is not None and available_seats is not None and available_seats > capacity:
            self.add_error('available_seats', 'Available seats cannot be more than capacity.')

        return cleaned_data


class FerryScheduleSeatForm(forms.ModelForm):
    class Meta:
        model = FerrySchedule
        fields = ('available_seats',)
        widgets = {
            'available_seats': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_available_seats(self):
        available_seats = self.cleaned_data['available_seats']
        if available_seats > self.instance.capacity:
            raise forms.ValidationError('Available seats cannot be more than capacity.')
        return available_seats
