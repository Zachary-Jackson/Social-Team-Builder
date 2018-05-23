from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm
from . import models


@login_required
def profile_edit(request):
    """Allows a profile to be edited"""
    # Checks to see if the user has a profile, and if not creates it.
    try:
        instance = request.user.profile
    except AttributeError:
        models.Profile(user=request.user).save()
        instance = request.user.profile

    form = ProfileForm(request.POST or None, instance=instance)

    # The form is currently not capturing images properly.
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('profiles:profile', pk=request.user.pk)

    return render(
        request, 'profiles/edit.html', {'form': form, 'profile': True})


def profile_view(request, pk):
    """Lets any user view a person's profile"""
    # Get the User model that matches the pk
    user_profile = get_object_or_404(get_user_model(), pk=pk)
    skills = [skill for skill in user_profile.profile.skills.all()]
    return render(
        request, 'profiles/profile.html',
        {'profile': True, 'user_profile': user_profile, 'skills': skills})