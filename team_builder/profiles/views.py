from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from . import forms
from . import models


"""Miscellaneous views"""


def homepage(request):
    """This is the homepage for the profiles app"""
    skills = models.Skill.objects.all()
    projects = models.Project.objects.all()
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


"""Profile related views"""


@login_required
def profile_edit(request):
    """Allows a profile to be edited"""
    instance = request.user.profile
    form = forms.ProfileForm(instance=instance)

    # The form is currently not capturing images properly.
    if request.method == 'POST':
        form = forms.ProfileForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('profiles:profile', pk=request.user.pk)

    return render(
        request, 'profiles/edit.html', {'form': form, 'current_tab': 'Profile'})


def profile_view(request, pk):
    """Lets any user view a person's profile"""
    # Get the User model that matches the pk
    user_profile = get_object_or_404(models.Profile, pk=pk)

    # Checks to see if the User has an avatar if not user default media
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
        # temporary only get first position
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
            'project_form': project_form,
            'position_form': position_form,
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
            position_form.save()
            project_form.save()

            # Get the saved position and add it to the project
            project = project_form.instance
            project.positions.add(position_form.instance)
            return redirect('profiles:project', pk=project.pk)

    return render(
        request,
        'profiles/project_edit.html',
        {'project_form': project_form, 'position_form': position_form})


def project_view(request, pk):
    """Lets any user view a project"""
    # Get the Project that matches the pk
    project = get_object_or_404(models.Project, pk = pk)
    return render(request, 'profiles/project.html', {'project': project})