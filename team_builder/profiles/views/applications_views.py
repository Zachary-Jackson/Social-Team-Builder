from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

# django-notifications-hq
from notifications.signals import notify

from .. import models


"""applications related views"""


def get_applicant(position, profile_pk: int):
    """
    Checks to see if an applicant is in a position if not 404
    Returns the found_applicant or 404

    :param position -- A Position model object
    :param profile_pk -- A primary key associated with a profile
    :return: found applicant
    """
    # Get and update the Applicants model
    found_applicant = ''

    for applicant in position.applicants.all():
        if applicant.applicant.pk == profile_pk:
            found_applicant = applicant
            break

    # If an applicant is not found, 404
    if not found_applicant:
        raise Http404("An applicant was not found.")

    return found_applicant


def get_projects_with_filled_or_unfilled_positions(is_filled: bool, request):
    """
    Searches all of the User's projects and checks if they have
    filled or unfilled positions in them
    Returns found projects

    :param is_filled -- Bool stating if a position is filled or not
    :param request -- Standard django view request
    :return: found projects
    """
    projects = models.Project.objects.all().filter(
        Q(owner=request.user) & Q(positions__filled=is_filled))
    return projects


def get_needed_skills_and_found_positions(
        request, is_accepted: bool, is_filled: bool):
    """
    Gets all of the User's Positions
    Finds all of the applicants using is_filled
    returns the found_skills and needed_positions

    :param request -- Standard django view request
    :param is_accepted -- Bool stating if an applicant is accepted
    :param is_filled -- Bool stating if a position is filled or open
    :return: found_positions and needed skills
    """
    # Get all of the desired skills for the projects
    found_positions = set()
    needed_skills = set()

    positions = models.Position.objects.all() \
        .filter(related_project__owner=request.user)

    for position in positions:

        if position.applicants.all() and position.filled == is_filled:
            for applicant in position.applicants.all():

                if applicant.accepted == is_accepted and \
                        not applicant.rejected:
                    found_positions.add(applicant)
                    needed_skills.add(position.skill)

    return found_positions, needed_skills


def if_owned_get_position_profile(request, position_pk: int, profile_pk: int):
    """
    Checks if the user owns the profile and position

    :param request -- Standard django view request
    :param position_pk -- Position object's pk
    :param profile_pk -- Profile object's pk
    :return: positions and profile or 404
    """
    user = request.user
    position = get_object_or_404(models.Position, pk=position_pk)
    profile = get_object_or_404(get_user_model(), pk=profile_pk)

    # if the current user does not own the project kick them out
    if user != position.related_project.owner:
        raise Http404("You do not own this project")

    return position, profile


@login_required
def applications(request):
    """This is the main applications page"""
    # Get projects that have all positions unfilled
    projects = get_projects_with_filled_or_unfilled_positions(False, request)

    # Get found_positions and needed_skills where the position is not filled
    found_positions, needed_skills = get_needed_skills_and_found_positions(
        request, is_accepted=False, is_filled=False
    )

    return render(
        request,
        'profiles/applications.html',
        {
            'found_positions': found_positions,
            'current_tab': 'Applications',  # navigation bar selector
            'needed_skills': needed_skills,
            'projects': projects
        })


@login_required
def applications_accept(request, position_pk: int, profile_pk: int):
    """
    Allows the owner of a project to accept an applicant
    Redirects to main applications page

    Keyword arguments:
    position_pk -- Position object's pk
    profile_pk -- Profile object's pk
    """

    # Get position, profile or 404
    position, profile = if_owned_get_position_profile(
        request, position_pk, profile_pk
    )

    # Find the applicant or 404
    found_applicant = get_applicant(position, profile_pk)

    # Update the Applicant object
    found_applicant.accepted = True
    found_applicant.save()

    # Update the Position object
    position.filled_by = profile
    position.save()

    # Create a notification to send to the applicant
    skill = position.skill
    project = position.related_project
    message = f'You have been accepted as a {skill} for the project: {project}'
    notify.send(profile, recipient=found_applicant.applicant, verb=message)

    return redirect('profiles:applications')


@login_required
def applications_reject(request, position_pk: int, profile_pk: int):
    """
    Allows the owner of a project to reject an applicant
    Redirects to main applications page

    Keyword arguments:
    position_pk -- Position object's pk
    profile_pk -- Profile object's pk
    """

    # Get position, profile or 404
    position, profile = if_owned_get_position_profile(
        request, position_pk, profile_pk
    )

    # Find the applicant or 404
    found_applicant = get_applicant(position, profile_pk)

    # Update the Applicant object
    found_applicant.accepted = False
    found_applicant.rejected = True
    found_applicant.save()

    # Create a notification to send to the applicant
    skill = position.skill
    project = position.related_project
    message = f'You have been rejected as a {skill} for the project: {project}'
    notify.send(profile, recipient=found_applicant.applicant, verb=message)

    return redirect('profiles:applications')


@login_required
def applications_request(request, pk: int):
    """
    Allows a user to submit an application request

    Keyword arguments:
    pk -- primary key for a Position object
    """
    # Ensures that the Position model exists or 404
    position = get_object_or_404(models.Position, pk=pk)
    user = request.user

    # If the user owns the project 404
    if user == position.related_project.owner:
        raise Http404("You own this project!")

    # If the user has already applied, prevent another application
    for applicant in position.applicants.all():
        if applicant.applicant == user:
            raise Http404("You can only apply once.")

    # Create an Applicant model
    applicant = models.Applicants.objects.create(
        applicant=user,
        position=position

    )

    # Attach the applicant to a Position
    position.applicants.add(applicant)
    position.save()

    # Create a notification to send to the project owner
    project = position.related_project
    message = f'There is a pending application for the project: {project}'
    notify.send(user, recipient=position.related_project.owner, verb=message)

    # Return the user back to the Project's page
    return redirect('profiles:project', pk=pk)


@login_required
def applications_view_accepted(request):
    """Shows the user all of the applicants they have accepted"""
    # Get projects that have all positions filled
    projects = get_projects_with_filled_or_unfilled_positions(True, request)

    # Get found_positions and needed_skills where the position is filled
    found_positions, needed_skills = get_needed_skills_and_found_positions(
        request, is_accepted=True, is_filled=True
    )

    return render(
        request,
        'profiles/templates/profiles/applicants_accepted.html',
        {
            'found_positions': found_positions,
            'current_tab': 'Applications',  # navigation bar selector
            'needed_skills': list(needed_skills),
            'projects': projects
        })


@login_required
def applications_view_rejected(request):
    """Shows the user all of the applicants they have rejected"""
    projects = []

    # Get all of the desired skills for the projects
    found_positions = set()
    needed_skills = set()

    # Get all of a user's positions
    positions = models.Position.objects.all() \
        .filter(related_project__owner=request.user)

    for position in positions:

        # If there are applicants in a position add the position to applicants
        if position.applicants.all():
            for applicant in position.applicants.all():
                if applicant.rejected:
                    found_positions.add(applicant)
                    projects.append(position.related_project)
                    needed_skills.add(position.skill)

    return render(
        request,
        'profiles/templates/profiles/applicants_rejected.html',
        {
            'found_positions': found_positions,
            'current_tab': 'Applications',  # navigation bar selector
            'needed_skills': list(needed_skills),
            'projects': projects
    })