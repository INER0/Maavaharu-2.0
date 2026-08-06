from django import forms
from django.db.models import Q
from django.utils import timezone
import re

from .models import (
    Event, SpecialThemeParkEvent, ThemeParkEntranceTicket, ThemeParkPromotion,
    ThemeParkTicket, WeeklyThemeParkEvent,
)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(file, initial) for file in data]
        return single_file_clean(data, initial)


class BaseEventStaffForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        capacity = cleaned_data.get('capacity')
        available_capacity = cleaned_data.get('available_capacity')

        if capacity is None and available_capacity is not None:
            self.add_error('available_capacity', 'Set total capacity before entering available capacity.')

        if capacity is not None and available_capacity is not None and available_capacity > capacity:
            self.add_error('available_capacity', 'Available capacity cannot be more than total capacity.')

        if capacity is not None and available_capacity is None:
            cleaned_data['available_capacity'] = capacity

        return cleaned_data


class WeeklyEventStaffForm(BaseEventStaffForm):
    images = MultipleImageField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'}),
        help_text='You can select more than one activity picture.',
    )
    weekdays = forms.MultipleChoiceField(
        choices=Event.Weekday.choices,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'weekday-checkbox-list'}),
        label='Weekdays',
    )

    class Meta:
        model = WeeklyThemeParkEvent
        fields = (
            'name', 'event_type', 'images', 'weekdays', 'description', 'time',
            'capacity', 'available_capacity', 'price',
        )
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'capacity': forms.NumberInput(attrs={'min': 1}),
            'available_capacity': forms.NumberInput(attrs={'min': 0}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time'].required = False
        self.fields['capacity'].required = False
        self.fields['available_capacity'].required = False
        self.fields['time'].label = 'Time (optional)'
        self.fields['capacity'].label = 'Capacity (optional)'
        self.fields['available_capacity'].label = 'Available capacity (optional)'

    def clean(self):
        cleaned_data = super().clean()
        weekdays = cleaned_data.get('weekdays')

        if not weekdays:
            self.add_error('weekdays', 'Choose at least one weekday for weekly activities.')

        return cleaned_data


class SpecialEventStaffForm(BaseEventStaffForm):
    images = MultipleImageField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'accept': 'image/*'}),
        help_text='You can select more than one event picture.',
    )

    class Meta:
        model = SpecialThemeParkEvent
        fields = (
            'name', 'event_type', 'images', 'description', 'date', 'time',
            'capacity', 'available_capacity', 'price',
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'capacity': forms.NumberInput(attrs={'min': 1}),
            'available_capacity': forms.NumberInput(attrs={'min': 0}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time'].required = True
        self.fields['capacity'].required = True
        self.fields['available_capacity'].required = False

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        capacity = cleaned_data.get('capacity')

        if not date:
            self.add_error('date', 'Choose the date for special events.')
        if not time:
            self.add_error('time', 'Choose the time for special events.')
        if capacity is None:
            self.add_error('capacity', 'Enter the capacity for special events.')

        return cleaned_data


class EventCapacityForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('available_capacity',)
        widgets = {
            'available_capacity': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_available_capacity(self):
        available_capacity = self.cleaned_data['available_capacity']
        if available_capacity is None:
            return available_capacity
        if self.instance.capacity is None:
            raise forms.ValidationError('Set total capacity before entering available capacity.')
        if available_capacity > self.instance.capacity:
            raise forms.ValidationError('Available capacity cannot be more than total capacity.')
        return available_capacity


class ActivityTicketSaleForm(forms.ModelForm):
    class Meta:
        model = ThemeParkTicket
        fields = ('event', 'quantity')
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event'].queryset = Event.objects.filter(
            Q(available_capacity__gt=0) | Q(available_capacity__isnull=True)
        ).order_by('schedule_type', 'weekday', 'date', 'time')
        self.fields['event'].empty_label = 'Choose an event'

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get('event')
        quantity = cleaned_data.get('quantity')

        if event and quantity and event.available_capacity is not None and quantity > event.available_capacity:
            self.add_error('quantity', 'Requested tickets exceed the available capacity.')

        return cleaned_data


class EntranceTicketSaleForm(forms.ModelForm):
    class Meta:
        model = ThemeParkEntranceTicket
        fields = ('visit_date', 'quantity')
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_visit_date(self):
        visit_date = self.cleaned_data['visit_date']
        if visit_date < timezone.now().date():
            raise forms.ValidationError('Visit date cannot be in the past.')
        return visit_date


class ThemeParkBookingUpdateForm(forms.ModelForm):
    class Meta:
        model = ThemeParkTicket
        fields = ('quantity',)
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError('Quantity must be at least 1.')
        return quantity


class ThemeParkEntranceTicketForm(forms.ModelForm):
    class Meta:
        model = ThemeParkEntranceTicket
        fields = ('visit_date', 'quantity')
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_visit_date(self):
        visit_date = self.cleaned_data['visit_date']
        if visit_date < timezone.now().date():
            raise forms.ValidationError('Visit date cannot be in the past.')
        return visit_date


class ThemeParkPromotionForm(forms.ModelForm):
    class Meta:
        model = ThemeParkPromotion
        fields = ('event', 'title', 'description', 'discount_percent', 'valid_until')
        widgets = {
            'discount_percent': forms.NumberInput(attrs={
                'min': 1,
                'max': 100,
                'placeholder': 'Leave blank for normal activity advertisement',
            }),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discount_percent'].required = False
        self.fields['discount_percent'].label = 'Discount percent (optional)'


class TicketValidationForm(forms.Form):
    ticket_type = forms.ChoiceField(
        choices=(
            ('activity', 'Activity / Event Ticket'),
            ('entrance', 'Entrance Ticket'),
        )
    )
    verification_code = forms.CharField(
        label='Verification ID',
        widget=forms.TextInput(attrs={'placeholder': 'Paste ticket UUID'}),
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


class ThemeParkTicketForm(forms.ModelForm):
    class Meta:
        model = ThemeParkTicket
        fields = ('event', 'quantity')
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        event_type = kwargs.pop('event_type', None)
        exclude_event_type = kwargs.pop('exclude_event_type', None)
        super().__init__(*args, **kwargs)
        queryset = Event.objects.filter(
            Q(available_capacity__gt=0) | Q(available_capacity__isnull=True)
        ).order_by(
            'schedule_type', 'weekday', 'date', 'time'
        )
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if exclude_event_type:
            queryset = queryset.exclude(event_type=exclude_event_type)
        self.fields['event'].queryset = queryset
        self.fields['event'].empty_label = 'Choose an event'

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get('event')
        quantity = cleaned_data.get('quantity')

        if event and quantity and event.available_capacity is not None and quantity > event.available_capacity:
            self.add_error('quantity', 'Requested tickets exceed the available capacity.')

        return cleaned_data
