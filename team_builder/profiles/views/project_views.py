from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .. import forms
from .. import models


def get_project_and_authenticate(request, pk):
    """Gets the logged in user and makes sure that the user owns
    the project

    If so: return project
    Else: raise 404"""
    project = get_object_or_404(models.Project, pk=pk)

    # Checks if the logged in user owns the project. If not kick them out.
    if project.owner.pk != request.user.pk:
        raise Http404("You do not own this project.")

    return project


"""Project related views"""


@login_required()
def project_delete(request, pk):
    """Allows a project owner to delete a project"""
    project = get_project_and_authenticate(request, pk)

    project.delete()
    return redirect('profiles:homepage')


@login_required()
def project_delete_confirmation(request, pk):
    """Checks if a user really want to delete a project"""
    project = get_project_and_authenticate(request, pk)

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

    project = get_project_and_authenticate(request, pk)

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
    """Checks to see if the logged in user owns this project.
    If so show special owner template. If not show normal project template"""
    # Get the Project that matches the pk
    project = get_object_or_404(models.Project, pk=pk)

    # Makes sure there is a logged in user
    try:
        request.user
    except AttributeError:
        pass
    else:
        if request.user == project.owner:
            return render(
                request,
                'profiles/project_view_owned.html',
                {'project': project}
            )
    # If no logged in user or the wrong user the following happens
    return render(request, 'profiles/project.html', {'project': project})


@login_required
def project_view_all(request):
    """Shows the user all of their Projects regardless of filled status"""
    projects = models.Project.objects.all().filter(owner=request.user)\
        .prefetch_related('positions__skill')

    # Get all of the desired skills for the projects
    needed_skills = set()

    positions = [project.positions.all() for project in projects]

    for position in positions:
        # Because positions is a list of queries we need to get
        # the first item with [0]
        needed_skills.add(position[0].skill)

    return render(
        request,
        'profiles/project_view_all.html',
        {
            'current_tab': 'My Projects',  # navigation bar selector
            'needed_skills': list(needed_skills),
            'projects': projects,
        }
    )