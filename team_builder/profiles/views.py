from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from . import forms
from . import models


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
        request, 'profiles/profile.html',
        {'current_tab': 'Profile', 'user_profile': user_profile, 'image_url': image_url})


"""Project related views"""


def project_view(request, pk):
    """Lets any user view a project"""
    # Get the Project that matches the pk
    project = get_object_or_404(models.Project, pk = pk)
    return render(request, 'profiles/project.html', {'project': project})


@login_required()
def project_edit(request, pk):
    """Allows only the project's owner to edit a project"""
    project = get_object_or_404(models.Project, pk=pk)

    # Checks if the logged in user owns the project. If not kick them out.
    if project.owner.pk != request.user.pk:
        raise Http404("You do not own this project.")

    project_form = forms.ProjectForm(instance=project)
    position_form = forms.PositionForm(instance=project)

    if request.method == 'POST':
        project_form = forms.ProjectForm(request.POST, instance=project)
        if project_form.is_valid():
            project_form.save()
            return redirect('profiles:project', pk=pk)

    return render(
        request,
        'profiles/project_edit.html',
        {'project_form': project_form, 'position_form': position_form,
         'project': project})