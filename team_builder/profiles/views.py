from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile_edit(request):
    """Alows a profile to be edited"""
    return render(request, 'profiles/edit.html', {'profile': True})


def profile_view(request):
    """Lets any user view a person's profile"""
    # Get all the skill for the user
    skills = [skill for skill in request.user.profile.skills.all()]
    return render(
        request, 'profiles/profile.html', {'profile': True, 'skills': skills})
