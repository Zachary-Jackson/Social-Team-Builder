from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile_edit(request):
    """Alows a profile to be edited"""
    return render(request, 'profiles/edit.html', {'profile': True})


def profile_view(request):
    """Lets any user view a person's profile"""
    return render(request, 'profiles/profile.html', {'profile': True})
