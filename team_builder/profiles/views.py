from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm
from . import models


@login_required
def login_router(request):
    """This checks to see if a Profile has been created.
    If not create and redirect to edit page"""
    # Checks to see if the user has a profile, and if not creates it.
    try:
        request.user.profile
    except AttributeError:
        models.Profile(user=request.user, username=request.user.email).save()
        # redirect to profile edit page
        return redirect('profiles:edit')
    else:
        # redirect to main profile page
        return redirect('profiles:profile', pk=request.user.pk)


@login_required
def profile_edit(request):
    """Allows a profile to be edited"""
    instance = request.user.profile
    form = ProfileForm(instance=instance)

    # The form is currently not capturing images properly.
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('profiles:profile', pk=request.user.pk)

    return render(
        request, 'profiles/edit.html', {'form': form, 'profile': True})


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
        {'profile': True, 'user_profile': user_profile, 'image_url': image_url})
