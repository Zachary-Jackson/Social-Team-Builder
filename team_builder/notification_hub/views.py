from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render


def get_notification_and_authenticate(request, pk: int):
    """
    Gets the logged in user and makes sure that the user owns
    the notification

    :param request: The standard django request object
    :param pk: The primary key of a user

    :return: If the user owns the notification, return notification
    :else: raise 404
    """
    user = request.user

    # Get the notification or 404
    notification = get_object_or_404(user.notifications, pk=pk)

    # If the user does not own the notification 404
    if notification.recipient == user:
        Http404('You do not own this notification')

    return notification


"""Notification Views"""


@login_required
def notifications(request):
    """
    This is the main notification view for a user

    :param request: The standard django request object

    :return: render request for 'notifications.html'
    """
    notification_query = (
        request.user.notifications.all().prefetch_related("actor")
    )

    return render(
        request,
        'notification_hub/notifications.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )


@login_required
def delete(request, pk: int):
    """
    Marks a notification as read and reroute back to
    notification_hub:unread

    :param request: The standard django request object
    :param pk: The primary key of a notification

    :return: redirect to 'notification_hub:deletion_view'
    """
    notification = get_notification_and_authenticate(request, pk)

    # mark the notification as read
    notification.delete()

    return redirect('notification_hub:deletion_view')


@login_required
def deletion_view(request):
    """
    Shows the user all read notifications that they can delete

    :param request: The standard django request object

    :return: render request for 'deletion.html'
    """
    notification_query = (
        request.user.notifications.read().prefetch_related('actor')
    )

    return render(
        request,
        'notification_hub/deletion.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )


@login_required
def mark_read(request, pk: int):
    """
    Marks a notification as read and reroute back to
    notification_hub:unread

    :param request: The standard django request object
    :param pk: The primary key of a notification

    :return: redirect to 'notification_hub:unread'
    """
    notification = get_notification_and_authenticate(request, pk)

    # mark the notification as read
    notification.mark_as_read()

    return redirect('notification_hub:unread')


@login_required
def mark_unread(request, pk: int):
    """
    Marks a notification as unread and reroute back to the route
    'notification_hub:read'

    :param request: The standard django request object
    :param pk: The primary key of a notification

    :return: redirect to 'notification_hub:read'
    """
    notification = get_notification_and_authenticate(request, pk)

    # mark the notification as read
    notification.mark_as_unread()

    return redirect('notification_hub:read')


@login_required
def read(request):
    """
    Shows the user all their opened notifications

    :param request: The standard django request object

    :return: render request 'read.html'
    """
    notification_query = (
        request.user.notifications.read().prefetch_related('actor')
    )

    return render(
        request,
        'notification_hub/read.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )


@login_required
def unread(request):
    """
    Shows the user all their unopened notifications

    :param request: The standard django request object

    :return: render request 'unread.html'
    """
    notification_query = (
        request.user.notifications.unread().prefetch_related('actor')
    )

    return render(
        request,
        'notification_hub/unread.html',
        {
            'current_tab': 'Notifications',
            'notification_query': notification_query
        }
    )
