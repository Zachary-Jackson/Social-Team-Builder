from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .. import models


"""Miscellaneous views"""


def homepage(request):
    """This is the homepage for the profiles app"""
    projects = models.Project.objects.all().prefetch_related(
        'positions__skill')
    skills = sorted(models.Skill.objects.all(), key=attrgetter('skill'))

    return render(
        request,
        'profiles/homepage.html',
        {'skills': skills, 'projects': projects})


@login_required
def login_router(request):
    """Check to see if the user's profile has been edited.
    If not: route to the profile edit page and attach skills
    Else: route to the main profile page"""

    user = request.user

    # Checks if an AllSkills model is attached to the user
    # If not create and send to edit page
    try:
        user = user.allskills
    except AttributeError:
        models.AllSkills.objects.create(
            user_id=user.pk
        )

        # Redirect to the main edit page
        return redirect('profiles:edit')

    else:
        # redirect to main profile page
        return redirect('profiles:profile', pk=request.user.pk)
