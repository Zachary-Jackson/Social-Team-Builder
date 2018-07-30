from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountViewsTests(TestCase):
    """This tests to see if account's views work"""
    def test_signup_post(self):
        """Ensures a user can signup."""
        resp = self.client.post(
            reverse('accounts:signup'),
            data={'email': 'test@test.com',
                  'username': 'user',
                  'password1': 'testpass', 'password2': 'testpass'}
        )

        # We should have one user now.
        user = get_user_model()
        self.assertEqual(len(user.objects.all()), 1)

        self.assertRedirects(resp, reverse('login'))