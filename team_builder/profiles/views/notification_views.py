from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

"""Notification Views"""


@login_required
def notifications(request):
    """This is the main notification view for a user"""
    notification_query = request.user.notifications.all()\
        .prefetch_related("actor")

    return render(
        request,
        'profiles/notifications.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )


@login_required
def notifications_delete(request, pk):
    """Marks a notification as read and reroute back to
     profiles:notifications_unread"""
    user = request.user

    # Get the notification or 404
    notification = get_object_or_404(user.notifications, pk=pk)

    # If the user does not own the notification 404
    if notification.recipient == user:
        Http404('You do not own this notification')

    # mark the notification as read
    notification.delete()

    return redirect('profiles:notifications_deletion_view')


@login_required
def notifications_deletion_view(request):
    """Shows the user all read notifications that they can delete"""
    notification_query = request.user.notifications.read()

    return render(
        request,
        'profiles/notifications_deletion.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )


@login_required
def notifications_mark_read(request, pk):
    """Marks a notification as read and reroute back to
     profiles:notifications_unread"""
    user = request.user

    # Get the notification or 404
    notification = get_object_or_404(user.notifications, pk=pk)

    # If the user does not own the notification 404
    if notification.recipient == user:
        Http404('You do not own this notification')

    # mark the notification as read
    notification.mark_as_read()

    return redirect('profiles:notifications_unread')


@login_required
def notifications_mark_unread(request, pk):
    """Marks a notification as unread and reroute back to
     profiles:notifications_read"""
    user = request.user

    # Get the notification or 404
    notification = get_object_or_404(user.notifications, pk=pk)

    # If the user does not own the notification 404
    if notification.recipient == user:
        Http404('You do not own this notification')

    # mark the notification as read
    notification.mark_as_unread()

    return redirect('profiles:notifications_read')


@login_required
def notifications_read(request):
    """Shows the user all their opened notifications"""
    notification_query = request.user.notifications.read()

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
    notification_query = request.user.notifications.unread()

    return render(
        request,
        'profiles/notifications_unread.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )
