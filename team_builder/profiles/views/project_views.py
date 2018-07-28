from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .. import forms
from .. import models


def create_initial_data(positions):
    """
    Creates the initial dictionary for a formset, based on send in positions
    Returns: data
    """
    initial = []
    for position in positions:
        initial.append({
            'skill': position.skill,
            'information': position.information
        })

    # If there is not data in initial prefill with blank data
    if not initial:
        initial.append({'skill': 0, 'information': ''})
    return initial


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

    return render(
        request,
        'profiles/project_delete_confirmation.html',
        {'project': project})


@login_required()
def project_edit(request, pk):
    """Allows only the project's owner to edit a project"""

    project = get_project_and_authenticate(request, pk)

    project_form = forms.ProjectForm(instance=project)

    # Get all of the positions for the project
    all_positions = project.positions.all()
    
    # Separate the filled and unfilled projects, so that users can't
    # edit the filled ones
    filled_positions = all_positions.filter(filled=True)
    unfilled_positions = all_positions.filter(filled=False)

    initial = create_initial_data(unfilled_positions)

    position_form = forms.PositionFormSet(initial=initial)

    if request.method == 'POST':
        project_form = forms.ProjectForm(request.POST, instance=project)

        position_form = forms.PositionFormSet(
            request.POST, request.FILES
        )

        print(position_form.is_valid())

        if project_form.is_valid() and position_form.is_valid():
            project_form.save()

            position_dict = position_form.cleaned_data

            # We need to have a list of positions that were not edited
            # All edited positions will be deleted
            unedited_position_pks = []

            positions_to_create = []

            for position in position_dict:
                # Check if form had any information
                if position:
                    # Get the found position using the dictionary kwargs
                    found_item = unfilled_positions.filter(**position)

                    # If we actually found anything we know we have an
                    # unedited position. We do not want to mark this one
                    # for deletion
                    if found_item:
                        unedited_position_pks.append(found_item[0].pk)
                    else:
                        positions_to_create.append(position)

            positions_marked_for_deletion = (
                unfilled_positions.exclude(id__in=unedited_position_pks)
            )
            positions_marked_for_deletion.delete()

            # For each new position create it, then add to the main project
            for item in positions_to_create:
                item['related_project'] = project
                new_position = models.Position(**item)
                new_position.save()
                project.positions.add(new_position)

            return redirect('profiles:project', pk=pk)

    return render(
        request,
        'profiles/project_edit.html',
        {
            'filled_positions': filled_positions,
            'position_form': position_form,
            'project_form': project_form,
            'project': project
        })


@login_required()
def project_new(request):
    """Allows for the creation of a new project"""
    project_form = forms.ProjectForm()
    data = {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '1',
        'form-MAX_NUM_FORMS': '',
        'form-0-skills': ''
    }

    position_form_set = formset_factory(forms.PositionForm)
    position_form = position_form_set(data)

    if request.method == 'POST':
        project_form = forms.ProjectForm(request.POST)
        position_form = forms.PositionFormSet(request.POST, request.FILES)
        if project_form.is_valid() and position_form.is_valid():
            project_form.save()
            project = project_form.instance

            positions_data = position_form.cleaned_data

            # For loop that goes through each position and creates it
            # then adds it the the project
            for dictionary in positions_data:

                # If a form is left empty pass
                try:
                    skill = dictionary['skill']
                    information = dictionary['information']
                except KeyError:
                    pass
                else:
                    # Create a position
                    position = models.Position.objects.create(
                        information=information,
                        related_project=project,
                        skill=skill
                    )
                    # add the position to the project
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