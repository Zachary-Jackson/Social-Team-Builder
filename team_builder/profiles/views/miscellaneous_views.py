from operator import attrgetter

from django.views.generic import ListView

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

# django-notifications-hq
from notifications.signals import notify

from ..forms import NewSkillFormSet
from .. import models


def create_skill_confirmation(user, skill: int):
    """
    Creates a SkillConfirmation object and sends a notification to
    all staff or admins that a new skill has been requested

    :param user: The user who will own the SkillConfirmation
    :param skill: The string of the skill
    """
    skill = models.SkillConfirmation.objects.create(creator=user, skill=skill)

    user_model = get_user_model()

    staff = user_model.objects.filter(is_staff=True, is_superuser=True)

    message = f'Pending skill: "{skill.skill}" waiting for approval'

    for person in staff:
        notify.send(user, recipient=person, verb=message)


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
        """Returns all Projects that have an unfilled position"""
        return (
            models.Project.objects.filter(
                positions__filled=False
            ).distinct().prefetch_related('positions__skill')
        )


@login_required
def login_router(request):
    """
    Check to see if the user's profile has been edited.

    If not: route to the profile edit page and attach skills
    Else: route to the main profile page
    """

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


@login_required
def new_skill(request):
    """
    Allows a user to request new skills.
    """
    user = request.user
    if request.POST:
        skills_form = NewSkillFormSet(request.POST)

        if skills_form.is_valid():
            skills_dict = skills_form.cleaned_data

            for skill in skills_dict:
                # Check if the skill already exists

                try:
                    found_skill = models.Skill.objects.get(
                        skill__icontains=skill['skill']
                    )

                except:
                    # Check if the user is a superuser or staff
                    # If so create
                    if user.is_staff or user.is_superuser:
                        latest_skill = models.Skill.objects.create(
                            skill=skill['skill']
                        )
                        user.allskills.skills.add(latest_skill)
                    else:
                        create_skill_confirmation(user, skill['skill'])

                else:
                    # Add the found skill to the user
                    user.allskills.skills.add(found_skill)

            return redirect('profiles:profile', pk=user.pk)

    initial = [{'skill': ''}]
    skills_form = NewSkillFormSet(initial=initial)
    return render(
        request,
        'profiles/new_skill.html',
        {
            'current_tab': 'Profile',  # navigation bar selector
            'skills_form': skills_form,
            'user': user
        }
    )
