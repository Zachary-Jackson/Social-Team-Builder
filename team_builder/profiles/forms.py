import random

from django import forms
from django.contrib.auth import get_user_model
from django.forms import formset_factory

from . import models

# CHOICES is the tuple that defines what colors a user can pick for their
# background color in the ProfileForm
CHOICES = [
    ('random', 'Random'),
    ('blue', 'Blue'),
    ('', 'Blue-Green'),
    ('green', 'Green'),
    ('orange', 'Orange'),
    ('red', 'Red'),
    ('pink', 'Pink'),
    ('purple', 'Purple'),
]


class SkillForm(forms.ModelForm):
    """Form for the AllSkills model"""

    class Meta:
        model = models.AllSkills
        fields = [
            'skills'
        ]
        labels = {
            'name': 'Skill'
        }


SkillFormSet = formset_factory(SkillForm, extra=0)


class ProjectForm(forms.ModelForm):
    """Form for the Project model"""
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Project Title'
        self.fields['description'].widget.attrs['placeholder'] = \
            'Project description...'
        self.fields['time_line'].widget.attrs['placeholder'] = \
            'Project time line...'
        self.fields['requirements'].widget.attrs['placeholder'] =\
            'Project Requirements...'

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
            'time_commitment',
            'information',
        ]

        widgets = {'information': forms.Textarea(attrs={'rows': 10})}


class EditPositionForm(PositionForm):
    """Subclass of PositionForm that bypasses a bug when the user submits
    the PositionFormSet when deleting a Position and does nothing else

    Could potentially allow a user to edit a newly created project
    to have no positions though."""

    def is_valid(self):
        """Allows the form to count as valid if no information is present"""
        valid = super(PositionForm, self).is_valid()

        if self['skill'].data == '' and self['information'].data == '':
            valid = True
        return valid


PositionFormSet = formset_factory(EditPositionForm, extra=0)


class UserForm(forms.ModelForm):
    """This is the form for the user portion of the user model"""
    honey_pot = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = get_user_model()
        fields = [
            'avatar',
            'bio',
            'color',
            'username'
        ]

        widgets = {'color': forms.Select(choices=CHOICES)}

    def clean_color(self):
        """If the color is random, choice a random color"""
        color = self.cleaned_data['color']
        if color == 'random':
            color = random.choice(CHOICES[1:])[0]
        return color

    def clean_honey_pot(self):
        """This creates a honeypot to get rid of some bots"""
        honey_pot = self.cleaned_data['honey_pot']
        if honey_pot == '':
            return honey_pot
        else:
            raise forms.ValidationError("Take that bot!")