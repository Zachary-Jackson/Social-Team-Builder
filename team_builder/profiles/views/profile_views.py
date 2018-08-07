from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .. import forms
from .. import models


def create_initial_data(user) -> list:
    """
    Creates the initial data dictionary for a formset, based on a user
    Returns: a list of skill pks

    Keyword arguments:
    user -- User model object
    """

    initial = []
    skills = user.allskills.skills.all()

    for skill in skills:
        initial.append({
            'skills': [skill.pk]  # select many field requires a list
        })

    # If skills is empty create a blank form
    if not initial:
        initial.append({'skills': 0})

    return initial


"""Profile related views"""


@login_required
def profile_edit(request):
    """Allows a profile to be edited"""
    instance = request.user

    if request.method == 'POST':
        breakpoint()
        profile_form = forms.UserForm(
            request.POST, request.FILES, instance=instance
        )
        skills_form = forms.SkillFormSet(
            request.POST, request.FILES
        )

        if profile_form.is_valid() and skills_form.is_valid():
            profile_form.save()
            skills_dict = skills_form.cleaned_data

            # Take all skills from the cleaned data, and put it in a list
            skills_list = []
            for dictionary in skills_dict:

                # If a form is left empty pass
                try:
                    for item in dictionary['skills']:
                        skills_list.append(item)
                except KeyError:
                    pass

            # dissociate all skills from a user
            instance.allskills.skills.clear()
            # creates a new set of skills for the user
            instance.allskills.skills.add(*skills_list)

            return redirect('profiles:profile', pk=request.user.pk)

    # Create all the necessary forms
    profile_form = forms.UserForm(instance=instance)
    initial = create_initial_data(instance)
    skills_form = forms.SkillFormSet(initial=initial)

    return render(
        request,
        'profiles/profile_edit.html',
        {
            'profile_form': profile_form,
            'skills_form': skills_form,
            'current_tab': 'Profile'  # navigation bar selector
        })


def profile_edit_image(request):
    """Allows a profile image to be edited"""
    return render(request, 'profiles/profile_image_edit.html')


def profile_view(request, pk: int):
    """
    Lets any user view a person's profile

    Keyword arguments:
    pk -- primary key for a User model object
    """
    # Get the User model that matches the pk
    user_profile = get_object_or_404(get_user_model(), pk=pk)
    # filter projects by the logged in user
    projects = models.Project.objects.all().filter(owner=pk)\
        .prefetch_related('positions__skill')

    return render(
        request,
        'profiles/profile.html',
        {
            'current_tab': 'Profile',  # navigation bar selector
            'projects': projects,
            'user_profile': user_profile
        }
    )