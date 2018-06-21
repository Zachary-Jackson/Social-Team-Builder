from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from . import forms
from . import models


"""Miscellaneous views"""


def homepage(request):
    """This is the homepage for the profiles app"""
    projects = models.Project.objects.all().prefetch_related('positions')
    skills = sorted(models.Skill.objects.all(), key=attrgetter('skill'))

    return render(
        request,
        'profiles/homepage.html',
        {'skills': skills, 'projects': projects})


@login_required
def login_router(request):
    """This checks to see if a Profile has been created.
    If not create and redirect to edit page"""
    try:
        request.user.profile
    except AttributeError:
        # create a Profile and redirect the user to the edit page
        models.Profile(user=request.user, username=request.user.email).save()
        return redirect('profiles:edit')
    else:
        # redirect to main profile page
        return redirect('profiles:profile', pk=request.user.pk)


"""applications related views"""


@login_required
def applications(request):
    """This is the main applications page"""
    # Get all of the logged in user's Projects
    projects = models.Project.objects.all()\
        .filter(owner=request.user.profile).prefetch_related('positions')

    # Get all of the desired skills for the projects
    needs = set()
    applicant_list = set()

    positions = models.Position.objects.all()\
        .filter(position_creator=request.user.profile)

    for position in positions:
        needs.add(position.skill)

        # If there are applicants in a position add the position to applicants
        if position.any_applicants:
            applicant_list.add(position)

    return render(
        request,
        'profiles/applications.html',
        {
            'applicant_list': applicant_list,
            'current_tab': 'Applications',
            'needs': list(needs),
            'projects': projects
        })


"""Profile related views"""


@login_required
def profile_edit(request):
    """Allows a profile to be edited"""
    instance = request.user.profile
    form = forms.ProfileForm(instance=instance)

    # The form is currently not capturing images properly.
    if request.method == 'POST':
        form = forms.ProfileForm(
            request.POST, request.FILES, instance=instance
        )

        if form.is_valid():
            form.save()
            return redirect('profiles:profile', pk=request.user.pk)

    return render(
        request, 'profiles/edit.html', {'form': form,
                                        'current_tab': 'Profile'})


def profile_view(request, pk):
    """Lets any user view a person's profile"""
    # Get the User model that matches the pk
    user_profile = get_object_or_404(models.Profile, pk=pk)

    # Checks to see if the User has an avatar if not use default media
    try:
        image_url = static(user_profile.avatar.url)
    except ValueError:
        image_url = static('profiles_media/default_profile_image.png')

    return render(
        request,
        'profiles/profile.html',
        {
            'current_tab': 'Profile',
            'user_profile': user_profile,
            'image_url': image_url})


"""Project related views"""


@login_required()
def project_delete(request, pk):
    """Allows a project owner to delete a project"""
    project = get_object_or_404(models.Project, pk=pk)

    # Checks if the logged in user owns the project. If not kick them out.
    if project.owner.pk != request.user.pk:
        raise Http404("You do not own this project.")

    project.delete()
    return redirect('profiles:homepage')


@login_required()
def project_delete_confirmation(request, pk):
    """Checks if a user really want to delete a project"""
    project = get_object_or_404(models.Project, pk=pk)

    # Checks if the logged in user owns the project. If not kick them out.
    if project.owner.pk != request.user.pk:
        raise Http404("You do not own this project.")

    if request.method == 'POST':
        # If the user deleted the project return to homepage
        if request.POST.get('delete'):
            return redirect('profiles:project_delete', pk=pk)

        # If the user went back, go to the edit screen
        if request.POST.get('back'):
            return redirect('profiles:project_edit', pk=pk)

    return render (
        request,
        'profiles/project_delete_confirmation.html',
        {'project': project})


@login_required()
def project_edit(request, pk):
    """Allows only the project's owner to edit a project"""
    project = get_object_or_404(models.Project, pk=pk)

    # Checks if the logged in user owns the project. If not kick them out.
    if project.owner.pk != request.user.pk:
        raise Http404("You do not own this project.")

    project_form = forms.ProjectForm(instance=project)
    # Currently only one position can be added per project. temporary
    position_form = forms.PositionForm(instance=project.positions.all()[0])

    if request.method == 'POST':
        project_form = forms.ProjectForm(request.POST, instance=project)

        # temporary, only get first position
        position_form = forms.PositionForm(
            request.POST, instance=project.positions.all()[0]
        )

        if project_form.is_valid() and position_form.is_valid():
            project_form.save()
            position_form.save()
            return redirect('profiles:project', pk=pk)

    return render(
        request,
        'profiles/project_edit.html',
        {
            'position_form': position_form,
            'project_form': project_form,
            'project': project
        })


@login_required()
def project_new(request):
    """Allows for the creation of a new project"""
    project_form = forms.ProjectForm()
    position_form = forms.PositionForm()

    if request.method == 'POST':
        project_form = forms.ProjectForm(request.POST)
        position_form = forms.PositionForm(request.POST)

        if project_form.is_valid() and position_form.is_valid():
            project_form.save()
            project = project_form.instance

            # Position needs to know which Project it belongs to
            position = position_form.save(commit=False)
            position.related_project = project
            position.save()

            # Get the saved position and add it to the project
            project.positions.add(position)
            return redirect('profiles:project', pk=project.pk)

    return render(
        request,
        'profiles/project_edit.html',
        {'project_form': project_form, 'position_form': position_form})


def project_view(request, pk):
    """Lets any user view a project"""
    # Get the Project that matches the pk
    project = get_object_or_404(models.Project, pk=pk)
    return render(request, 'profiles/project.html', {'project': project})


"""searching related views"""


def search(request):
    """Searches all projects and returns the results"""
    search_term = request.GET.get('search_term')

    # If no search term is provided reroute to homepage
    if not search_term:
        return redirect('profiles:homepage')

    projects = models.Project.objects.all().prefetch_related('positions')\
        .filter(
            Q(title__icontains=search_term) |
            Q(time_line__icontains=search_term) |
            Q(requirements__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(positions__information__icontains=search_term)
    ).distinct()

    skills = sorted(models.Skill.objects.all(), key=attrgetter('skill'))

    # Creates what search results information is shown to the user.
    if not projects:
        search_results = 'No results were found with: {}'.format(search_term)
    else:
        search_results = '{} results were found with: {}'.format(
            len(projects), search_term)

    return render(
        request,
        'profiles/homepage.html',
        {
            'skills': skills, 'projects': projects,
            'search_results': search_results}
    )


def search_by_skill(request, skill):
    """Searches projects by skills needed"""
    # The skill might be in a url acceptable format without spaces
    # if so we need to remove the spaces
    # See Skill's readable_to_url method
    skill = skill.replace('_', ' ')

    skills = models.Skill.objects.all()
    sorted_skills = sorted(skills, key=attrgetter('skill'))

    # If the searched skill is not in skills, return no results
    try:
        skills.get(skill=skill)
    except models.Skill.DoesNotExist:
        search_results = 'No results were found with the skill: {}'\
            .format(skill)

        return render(request, 'profiles/homepage.html',
                      {'search_results': search_results,
                       'skills': sorted_skills})

    # Get all projects that need a position with the searched skill
    projects = models.Project.objects.all().filter(
        Q(positions__skill__skill__contains=skill)).distinct()

    # Creates what search results information is shown to the user.
    if not projects:
        search_results = 'No results were found with the skill: {}'\
            .format(skill)
    else:
        search_results = '{} results for the skill: {}'.format(
            len(projects), skill)

    return render(request, 'profiles/homepage.html',
                  {'projects': projects,
                   'search_results': search_results,
                   'skills': sorted_skills})
