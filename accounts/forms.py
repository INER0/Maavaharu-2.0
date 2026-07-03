from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class VisitorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=20)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.VISITOR
        if commit:
            user.save()
        return user
