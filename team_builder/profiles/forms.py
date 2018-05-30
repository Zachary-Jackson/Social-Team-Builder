from django import forms

from . import models


class ProfileForm(forms.ModelForm):
    """This is the form for the profile model"""
    honey_pot = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = models.Profile
        fields = [
            'avatar',
            'bio',
            'skills',
            'username'
        ]

    def clean_honey_pot(self):
        """This creates a honeypot to get rid of some bots"""
        honey_pot = self.cleaned_data['honey_pot']
        if honey_pot == '':
            return honey_pot
        else:
            raise forms.ValidationError("Take that bot!")