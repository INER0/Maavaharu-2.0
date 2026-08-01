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
        fields = ('title', 'content', 'image', 'image_url', 'is_active')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'image_url': 'Image URL (optional fallback)',
            'is_active': 'Show on homepage',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image_url'].required = False


class MapLocationForm(forms.ModelForm):
    class Meta:
        model = MapLocation
        fields = ('name', 'category', 'description', 'image', 'latitude', 'longitude', 'pin_x', 'pin_y')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'pin_x': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.1, 'placeholder': 50}),
            'pin_y': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.1, 'placeholder': 50}),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pin_x'].required = False
        self.fields['pin_y'].required = False

    def clean_pin_x(self):
        pin_x = self.cleaned_data.get('pin_x')
        if pin_x is None:
            return 50
        if pin_x < 0 or pin_x > 100:
            raise forms.ValidationError('Pin X must be between 0 and 100.')
        return pin_x

    def clean_pin_y(self):
        pin_y = self.cleaned_data.get('pin_y')
        if pin_y is None:
            return 50
        if pin_y < 0 or pin_y > 100:
            raise forms.ValidationError('Pin Y must be between 0 and 100.')
        return pin_y


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


class AdminUserCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text='Temporary password for the new account.',
    )

    class Meta:
        model = get_user_model()
        fields = (
            'username', 'email', 'phone', 'role', 'password',
            'is_active', 'is_staff', 'is_superuser',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].initial = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('role', 'is_active', 'is_staff', 'is_superuser')
