from operator import attrgetter

from django.views.generic import ListView

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .. import models


"""Miscellaneous views"""


class HomepageListView(ListView):
    """This is the homepage for the profiles app"""
    model = models.Project
    template_name = 'profiles/homepage.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        # gets skills for the template
        context = super(HomepageListView, self).get_context_data(**kwargs)
        context['skills'] = (
            sorted(models.Skill.objects.all(), key=attrgetter('skill'))
        )
        return context

    def get_queryset(self):
        return (
            models.Project.objects.all().prefetch_related('positions__skill')
        )


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
