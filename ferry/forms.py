from django import forms
import re

from .models import FerrySchedule


class FerryScheduleForm(forms.ModelForm):
    weekdays = forms.MultipleChoiceField(
        choices=FerrySchedule.Weekday.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Weekly days',
    )

    class Meta:
        model = FerrySchedule
        fields = (
            'route_name', 'origin', 'destination', 'schedule_type', 'weekdays',
            'date', 'departure_time', 'return_time', 'capacity', 'available_seats',
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
            'return_time': forms.TimeInput(attrs={'type': 'time'}),
            'capacity': forms.NumberInput(attrs={'min': 1}),
            'available_seats': forms.NumberInput(attrs={'min': 0}),
        }

    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get('capacity')
        available_seats = cleaned_data.get('available_seats')
        schedule_type = cleaned_data.get('schedule_type')
        weekdays = cleaned_data.get('weekdays')
        schedule_date = cleaned_data.get('date')

        if capacity is not None and available_seats is not None and available_seats > capacity:
            self.add_error('available_seats', 'Available seats cannot be more than capacity.')

        if schedule_type == FerrySchedule.ScheduleType.WEEKLY and not weekdays:
            self.add_error('weekdays', 'Choose at least one weekday for a weekly ferry schedule.')

        if schedule_type == FerrySchedule.ScheduleType.SPECIAL and not schedule_date:
            self.add_error('date', 'Choose the date for a special ferry schedule.')

        if schedule_type in [FerrySchedule.ScheduleType.DAILY, FerrySchedule.ScheduleType.WEEKLY]:
            cleaned_data['date'] = None

        if schedule_type != FerrySchedule.ScheduleType.WEEKLY:
            cleaned_data['weekdays'] = []

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['return_time'].required = False
        self.fields['return_time'].label = 'Return time (optional)'


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


class FerryBookingValidationForm(forms.Form):
    verification_code = forms.CharField(
        label='Hotel booking verification ID',
        widget=forms.TextInput(attrs={'placeholder': 'Paste hotel booking UUID'}),
        required=False,
    )
    username = forms.CharField(
        label='Or search visitor name/username',
        widget=forms.TextInput(attrs={'placeholder': 'Customer username or name'}),
        required=False,
    )

    def clean_verification_code(self):
        value = self.cleaned_data.get('verification_code', '').strip()
        if not value:
            return ''
        match = re.search(
            r'[0-9a-fA-F]{8}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{4}-?[0-9a-fA-F]{12}',
            value,
        )
        if not match:
            raise forms.ValidationError('Paste a valid UUID verification ID.')
        raw_uuid = match.group(0).replace('-', '')
        return f'{raw_uuid[0:8]}-{raw_uuid[8:12]}-{raw_uuid[12:16]}-{raw_uuid[16:20]}-{raw_uuid[20:32]}'

    def clean(self):
        cleaned_data = super().clean()
        verification_code = cleaned_data.get('verification_code')
        username = cleaned_data.get('username', '').strip()
        if not verification_code and not username:
            raise forms.ValidationError('Enter a verification ID or visitor name/username.')
        cleaned_data['username'] = username
        return cleaned_data
