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


class ProjectForm(forms.ModelForm):
    """Form for the Project model"""
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Project Title'
        self.fields['description'].widget.attrs['placeholder'] = \
            'Project description...'
        self.fields['time_line'].widget.attrs['placeholder'] = \
            'Project time line...'

    class Meta:
        model = models.Project
        fields = [
            'owner',
            'title',
            'time_line',
            'requirements',
            'description'
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 13, 'cols': 20}),
            'requirements': forms.Textarea(attrs={'rows': 7, 'cols': 20})}


class PositionForm(forms.ModelForm):
    """Form for the Position model"""
    def __init__(self, *args, **kwargs):
        super(PositionForm, self).__init__(*args, **kwargs)
        self.fields['information'].widget.attrs['placeholder'] = \
            'Position Information...'

    class Meta:
        model = models.Position
        fields = [
            'skill',
            'information',
        ]

        widgets = {'information': forms.Textarea(attrs={'rows': 10})}
