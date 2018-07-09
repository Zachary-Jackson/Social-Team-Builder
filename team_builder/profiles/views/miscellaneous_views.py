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
    """Check to see if a Profile has been created.
    If not create and redirect to edit page"""
    try:
        request.user.profile
    except AttributeError:
        # create a Profile and redirect the user to the edit page
        models.Profile(user=request.user, username=request.user.email).save()
        return redirect('profiles:edit')
    else:
        # redirect to main profile page
        return redirect('profiles:profile', pk=request.user.profile.pk)