from django import forms

from . import models


class ProfileForm(forms.ModelForm):
    """This is the form for the profile model"""

    class Meta:
        model = models.Profile
        fields = [
            'avatar',
            'bio',
            'skills'
        ]
