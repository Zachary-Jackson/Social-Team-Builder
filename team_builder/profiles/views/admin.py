from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render


from .. import models


def admin_or_staff(user) -> bool:
    """
    Checks to see if a user is an admin or staff

    :param user: Standard User model
    :return: Bool stating if the user is an admin or staff
    """
    if user.is_staff or user.is_superuser:
        return True
    return False


@login_required
def administrative(request):
    """
    Shows an Admin/staff user the administrative page

    :param request: Standard django request object
    :return: render 'profiles/administrative.html'
    """
    logged_in_user = request.user
    if not admin_or_staff(logged_in_user):
        raise Http404('You are not an admin or staff user!')

    tasks = models.SkillConfirmation.objects.filter(pending=True)

    return render(
        request,
        'profiles/administrative.html',
        {
            'current_tab': 'Administrative',  # navigation bar selector
            'tasks': tasks

        }
    )


@login_required
def administrative_non_pending(request):
    """
    Shows an Admin/staff user the administrative page for non_pending items
    """
    logged_in_user = request.user
    if not admin_or_staff(logged_in_user):
        raise Http404('You are not an admin or staff user!')

    tasks = (
        models.SkillConfirmation.objects.filter(pending=False).order_by('-pk')
    )

    return render(
        request,
        'profiles/administrative_non_pending.html',
        {
            'current_tab': 'Administrative',  # navigation bar selector
            'tasks': tasks

        }
    )


@login_required
def skill_accept(request, pk: int):
    """
    Creates a Skill object From a SkillConfirmation object
    The new skill is added to the creator's AllSkills model

    :param request: Standard django request object
    :param pk: The pk of a SkillConfirmation object
    :return: redirect to 'profiles:administrative'
    """
    logged_in_user = request.user
    if not admin_or_staff(logged_in_user):
        raise Http404('You are not an admin or staff user!')

    skill_confirmation = get_object_or_404(models.SkillConfirmation, pk=pk)
    skill = models.Skill.objects.get_or_create(skill=skill_confirmation.skill)

    user = skill_confirmation.creator
    user.allskills.skills.add(skill[0])  # Skill is a tuple

    skill_confirmation.pending = False
    skill_confirmation.accepted = True
    skill_confirmation.save()

    return redirect('profiles:administrative')


@login_required
def skill_deny(request, pk: int):
    """
    Denys a SkillConfirmation request and closes the request

    :param request: Standard django request object
    :param pk: The pk of a SkillConfirmation object
    :return: render redirect to 'profiles:administrative'
    """
    logged_in_user = request.user
    if not admin_or_staff(logged_in_user):
        raise Http404('You are not an admin or staff user!')

    skill_confirmation = get_object_or_404(models.SkillConfirmation, pk=pk)
    skill_confirmation.pending = False
    skill_confirmation.save()

    return redirect('profiles:administrative')