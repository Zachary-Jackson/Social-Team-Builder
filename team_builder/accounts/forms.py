from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class UserCreateForm(UserCreationForm):
    """A form that gets the required fields for a custom user model"""
    honey_pot = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = get_user_model()
        fields = ("email", "username", "password1", "password2")
        help_texts = {
            'email': None,
            'username': None,
            'password1': None,
            'password2': None
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Email address"

    def clean_honey_pot(self):
        """This creates a honeypot to get rid of some bots"""
        honey_pot = self.cleaned_data['honey_pot']
        if honey_pot == '':
            return honey_pot
        else:
            raise forms.ValidationError("Take that bot!")
