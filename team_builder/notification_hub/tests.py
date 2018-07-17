from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# django-notifications-hq
from notifications.signals import notify


class NotificationHubViewsTests(TestCase):
    """This tests to see if notifications_hub's views work"""
    def setUp(self):
        """Creates a Profile and some skills for testing"""

        # Get the current User model
        user = get_user_model()

        # Create the first user for testing
        self.user = user.objects.create_user(
            email='user@user.com',
            username='Santa',
            password='testpass'
        )

        # Creates a second user
        user = get_user_model()
        self.user_2 = user.objects.create_user(
            email='user2@user2.com',
            username='Hattie',
            password='testpass',
        )

        # Create a message to send to self.user
        self.occupation = 'Django Developer'
        self.project = 'Test Project'
        self.message_1 = (
            f'You are a {self.occupation} for the project: {self.project}!'
        )

        # Accepted message unread
        notify.send(
            self.user_2,
            recipient=self.user,
            verb=self.message_1
        )

        # Declined message read
        self.message_2 = (
            f'You have been rejected as a {self.occupation} for the '
            f'project: {self.project}'
        )

        notify.send(
            self.user_2,
            recipient=self.user,
            verb=self.message_2
        )
        self.user.notifications.get(pk=2).mark_as_read()

    """Notification tests"""

    def test_notifications(self):
        """Ensures the main notifications view is working"""
        self.client.login(username='user@user.com', password='testpass')

        resp = self.client.get(reverse('notification_hub:notifications'))

        # various page information
        self.assertContains(resp, 'Notifications')
        self.assertContains(resp, 'Unread')
        self.assertContains(resp, 'Read')
        self.assertContains(resp, 'Deletion View')
        self.assertContains(resp, 'Time of notification')
        # notification information
        self.assertContains(resp, self.message_1)
        self.assertContains(resp, f'Unread from: {self.user_2}')
        self.assertContains(resp, self.message_2)
        self.assertContains(resp, f'Read from: {self.user_2}')

        self.assertTemplateUsed('profiles/notifications.html')

    def test_notification_delete(self):
        """Ensures that a user can delete a notification"""
        self.client.login(username='user@user.com', password='testpass')

        resp = self.client.get(
            reverse('notification_hub:delete',
                    kwargs={'pk': 1}))

        self.assertEqual(len(self.user.notifications.all()), 1)
        self.assertRedirects(
            resp,
            reverse('notification_hub:deletion_view')
        )

    def test_notifications_deletion_view(self):
        """Ensures the read notifications view is working"""
        self.client.login(username='user@user.com', password='testpass')

        resp = self.client.get(reverse('notification_hub:deletion_view'))

        # various page information
        self.assertContains(resp, 'Notifications')
        self.assertContains(resp, 'Unread')
        self.assertContains(resp, 'Read')
        self.assertContains(resp, 'Deletion View')
        self.assertContains(resp, 'Read notifications for deletion')
        self.assertContains(resp, 'Time of notification')
        # notification information
        self.assertContains(resp, self.message_2)
        self.assertContains(resp, 'Delete')
        self.assertContains(resp, f'From: {self.user_2}')

        self.assertTemplateUsed('profiles/notifications_deletion.html')

    def test_notification_mark_read(self):
        """Ensures that a user can mark a notification as read"""
        self.client.login(username='user@user.com', password='testpass')

        resp = self.client.get(
            reverse('notification_hub:mark_read',
                    kwargs={'pk': 1}))

        # We should not have deleted a notification
        self.assertEqual(len(self.user.notifications.all()), 2)
        self.assertEqual(self.user.notifications.get(pk=1).unread, False)

        self.assertRedirects(
            resp,
            reverse('notification_hub:unread')
        )

    def test_notification_mark_unread(self):
        """Ensures that a user can mark a notification as unread"""
        self.client.login(username='user@user.com', password='testpass')

        resp = self.client.get(
            reverse('notification_hub:mark_unread',
                    kwargs={'pk': 2}))

        # We should not have deleted a notification
        self.assertEqual(len(self.user.notifications.all()), 2)
        self.assertEqual(self.user.notifications.get(pk=2).unread, True)

        self.assertRedirects(
            resp,
            reverse('notification_hub:read')
        )

    def test_notifications_read(self):
        """Ensures the read notifications view is working"""
        self.client.login(username='user@user.com', password='testpass')

        resp = self.client.get(reverse('notification_hub:read'))

        # various page information
        self.assertContains(resp, 'Notifications')
        self.assertContains(resp, 'Unread')
        self.assertContains(resp, 'Read')
        self.assertContains(resp, 'Deletion View')
        self.assertContains(resp, 'Read Notifications')
        self.assertContains(resp, 'Time of notification')
        # notification information
        self.assertContains(resp, self.message_2)
        self.assertContains(resp, 'Mark unread')
        self.assertContains(resp, f'From: {self.user_2}')

        self.assertTemplateUsed('profiles/notifications_read.html')

    def test_notifications_unread(self):
        """Ensures the unread notifications view is working"""
        self.client.login(username='user@user.com', password='testpass')

        resp = self.client.get(reverse('notification_hub:unread'))

        # various page information
        self.assertContains(resp, 'Notifications')
        self.assertContains(resp, 'Unread')
        self.assertContains(resp, 'Read')
        self.assertContains(resp, 'Deletion View')
        self.assertContains(resp, 'Unread Notifications')
        self.assertContains(resp, 'Time of notification')
        # notification information
        self.assertContains(resp, self.message_1)
        self.assertContains(resp, 'Mark read')
        self.assertContains(resp, f'From: {self.user_2}')

        self.assertTemplateUsed('profiles/notifications_unread.html')

