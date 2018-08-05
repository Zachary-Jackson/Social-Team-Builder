import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from . import models


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

        self.assertRedirects(resp, reverse('accounts:email_confirmation'))

    def test_token_confirmation_view(self):
        """
        Ensures that the token_confirmation_view works and toggles
        a user to be active.
        """
        # Create a user that is inactive
        user_model = get_user_model()
        user = user_model.objects.create_user(
            'test@test.com', 'user', 'testpass'
        )

        # User should not be active
        self.assertFalse(user.is_active)

        # Create a fake token for the user
        token = 'token'
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=1)
        models.AuthenticationToken(
            user=user,
            token=token,
            expiration_date=expiration_date
        ).save()

        resp = self.client.get(
            reverse('accounts:token_confirmation',
                    kwargs={'token': 'token'})
        )

        # Ensure that the user is active
        user = user_model.objects.get(email='test@test.com')
        self.assertTrue(user.is_active)

        self.assertEqual(resp.status_code, 302)
