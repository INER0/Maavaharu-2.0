from django import forms

from .models import Event, ThemeParkTicket


class ThemeParkTicketForm(forms.ModelForm):
    class Meta:
        model = ThemeParkTicket
        fields = ('event', 'quantity')
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        event_type = kwargs.pop('event_type', None)
        super().__init__(*args, **kwargs)
        queryset = Event.objects.filter(available_capacity__gt=0).order_by('date', 'time')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        self.fields['event'].queryset = queryset
        self.fields['event'].empty_label = 'Choose an event'

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get('event')
        quantity = cleaned_data.get('quantity')

        if event and quantity and quantity > event.available_capacity:
            self.add_error('quantity', 'Requested tickets exceed the available capacity.')

        return cleaned_data
