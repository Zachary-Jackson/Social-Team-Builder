from django.contrib.auth.decorators import login_required
from django.shortcuts import render

"""Notification Views"""


@login_required
def notifications(request):
    """This is the main notification view for a user"""
    notification_query = request.user.notifications.all()\
        .prefetch_related('actor__profile')

    return render(
        request,
        'profiles/notifications.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )


@login_required
def notifications_read(request):
    """Shows the user all their opened notifications"""
    notification_query = request.user.notifications.read()\
        .prefetch_related('actor__profile')

    return render(
        request,
        'profiles/notifications_read.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )


@login_required
def notifications_unread(request):
    """Shows the user all their unopened notifications"""
    notification_query = request.user.notifications.unread()\
        .prefetch_related('actor__profile')

    return render(
        request,
        'profiles/notifications_unread.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )
