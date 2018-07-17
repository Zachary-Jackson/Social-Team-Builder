from django.urls import path

from . import views

app_name = 'notification_hub'

urlpatterns = [
    path('all/', views.notifications, name='notifications'),
    path(
        'deletion/<int:pk>',
        views.delete,
        name='delete'
    ),
    path(
        'deletion_view',
        views.deletion_view,
        name='deletion_view'
    ),
    path(
        'mark_read/<int:pk>/',
        views.mark_read,
        name='mark_read'
    ),
    path(
        'mark_unread/<int:pk>/',
        views.mark_unread,
        name='mark_unread'
    ),
    path(
        'unread',
        views.unread,
        name='unread'
    ),
    path(
        'read',
        views.read,
        name='read'
    ),
]