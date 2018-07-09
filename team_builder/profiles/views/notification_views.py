from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .. import forms
from .. import models

"""Notification Views"""


def notifications(request):
    """This is the main notification view for a user"""

    return render(
        request,
        'profiles/notifications.html',
        {'notifications_tab': 'All'}
    )
