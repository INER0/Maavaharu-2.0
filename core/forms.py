from django import forms
from django.contrib.auth import get_user_model

from .models import Advertisement, MapImage, MapLocation, SystemIssue


class MockPaymentForm(forms.Form):
    cardholder_name = forms.CharField(max_length=120)
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={'placeholder': '4242 4242 4242 4242'}),
    )
    expiry = forms.CharField(
        max_length=7,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YYYY'}),
    )
    cvv = forms.CharField(
        max_length=4,
        widget=forms.PasswordInput(attrs={'placeholder': '123'}),
    )

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number'].replace(' ', '')
        if not card_number.isdigit() or len(card_number) < 12:
            raise forms.ValidationError('Enter a valid card number for the mock payment.')
        return card_number

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not cvv.isdigit() or len(cvv) not in [3, 4]:
            raise forms.ValidationError('Enter a valid CVV.')
        return cvv


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ('title', 'content', 'image_url', 'is_active')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }


class MapLocationForm(forms.ModelForm):
    class Meta:
        model = MapLocation
        fields = ('name', 'category', 'description', 'latitude', 'longitude', 'pin_x', 'pin_y')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'pin_x': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.1}),
            'pin_y': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.1}),
        }
        labels = {
            'pin_x': 'Pin X position (%)',
            'pin_y': 'Pin Y position (%)',
        }
        help_texts = {
            'latitude': 'Real latitude shown to visitors when they click the pin.',
            'longitude': 'Real longitude shown to visitors when they click the pin.',
            'pin_x': '0 is left side of the image, 100 is right side.',
            'pin_y': '0 is top of the image, 100 is bottom.',
        }


class MapImageForm(forms.ModelForm):
    class Meta:
        model = MapImage
        fields = ('title', 'image', 'is_active')


class SystemIssueForm(forms.ModelForm):
    class Meta:
        model = SystemIssue
        fields = ('title', 'description', 'status')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('role', 'is_active', 'is_staff', 'is_superuser')
