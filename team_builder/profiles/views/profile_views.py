from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static

from django.shortcuts import get_object_or_404, redirect, render

from .. import forms
from .. import models


"""Profile related views"""


@login_required
def profile_edit(request):
    """Allows a profile to be edited"""
    instance = request.user
    profile_form = forms.UserForm(instance=instance)
    skills_form = forms.SkillForm(instance=instance.allskills)

    # The form is currently not capturing images properly.
    if request.method == 'POST':
        profile_form = forms.UserForm(
            request.POST, request.FILES, instance=instance
        )

        if profile_form.is_valid():
            profile_form.save()
            return redirect('profiles:profile', pk=request.user.pk)

    return render(
        request,
        'profiles/templates/profiles/profile_edit.html',
        {
            'profile_form': profile_form,
            'skills_form': skills_form,
            'current_tab': 'Profile'  # navigation bar selector
        })


def profile_view(request, pk):
    """Lets any user view a person's profile"""
    # Get the User model that matches the pk
    user_profile = get_object_or_404(get_user_model(), pk=pk)
    projects = models.Project.objects.all().filter(owner=pk)\
        .prefetch_related('positions__skill')

    # Checks to see if the User has an avatar if not use default media
    try:
        image_url = static(user_profile.avatar.url)
    except ValueError:
        image_url = static('profiles_media/default_profile_image.png')

    return render(
        request,
        'profiles/profile.html',
        {
            'current_tab': 'Profile',  # navigation bar selector
            'image_url': image_url,
            'projects': projects,
            'user_profile': user_profile})
