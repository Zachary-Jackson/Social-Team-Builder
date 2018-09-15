from django.shortcuts import get_object_or_404, redirect, render

from .. import models
from ..decorators import logged_in_admin_or_staff_required


@logged_in_admin_or_staff_required
def administrative(request):
    """
    Shows an Admin/staff user the administrative page

    :param request: Standard django request object
    :return: render 'profiles/administrative.html'
    """

    tasks = models.SkillConfirmation.objects.filter(pending=True)\
        .prefetch_related('creator')

    return render(
        request,
        'profiles/administrative.html',
        {
            'current_tab': 'Administrative',  # navigation bar selector
            'tasks': tasks

        }
    )


@logged_in_admin_or_staff_required
def administrative_non_pending(request):
    """
    Shows an Admin/staff user the administrative page for non_pending items

    :param request: Standard django request object
    :return: render 'profiles/administrative_non_pending.html'
    """

    tasks = (
        models.SkillConfirmation.objects
        .filter(pending=False)
        .order_by('-pk')
        .prefetch_related('creator')
             )

    return render(
        request,
        'profiles/administrative_non_pending.html',
        {
            'current_tab': 'Administrative',  # navigation bar selector
            'tasks': tasks

        }
    )


@logged_in_admin_or_staff_required
def skill_accept(request, pk: int):
    """
    Creates a Skill object From a SkillConfirmation object
    The new skill is added to the creator's AllSkills model

    :param request: Standard django request object
    :param pk: The pk of a SkillConfirmation object
    :return: redirect to 'profiles:administrative'
    """

    skill_confirmation = get_object_or_404(models.SkillConfirmation, pk=pk)
    skill = models.Skill.objects.get_or_create(skill=skill_confirmation.skill)

    user = skill_confirmation.creator
    user.allskills.skills.add(skill[0])  # Skill is a tuple

    skill_confirmation.pending = False
    skill_confirmation.accepted = True
    skill_confirmation.save()

    return redirect('profiles:administrative')


@logged_in_admin_or_staff_required
def skill_deny(request, pk: int):
    """
    Denys a SkillConfirmation request and closes the request

    :param request: Standard django request object
    :param pk: The pk of a SkillConfirmation object
    :return: render redirect to 'profiles:administrative'
    """

    skill_confirmation = get_object_or_404(models.SkillConfirmation, pk=pk)
    skill_confirmation.pending = False
    skill_confirmation.save()

    return redirect('profiles:administrative')