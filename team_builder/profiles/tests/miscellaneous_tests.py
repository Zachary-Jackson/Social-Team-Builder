from django.contrib.auth import get_user_model
from django.urls import reverse

from .base_tests import BaseTestWithPositionsProjects


class MiscellaneousTests(BaseTestWithPositionsProjects):
    """Tests all the views from miscellaneous_views"""

    def test_homepage(self):
        """Tests the homepage's content"""
        resp = self.client.get(reverse('profiles:homepage'))

        # projects that need field and their needs
        self.assertContains(resp, 'Test Project')
        self.assertContains(resp, 'Django developer')
        # various page information
        self.assertContains(resp, 'Projects')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Project Title')
        # The skills should be found under the All Needs section
        self.assertContains(resp, self.skill_1)
        self.assertContains(resp, self.skill_2)

        self.assertTemplateUsed('homepage.html')

    def test_login_router_with_profile(self):
        """Tests the router if the user has an AllSkills model attached"""
        self.client.login(username='user@user.com', password='testpass')
        resp = self.client.get(reverse('profiles:login_router'))
        self.assertRedirects(
            resp, reverse('profiles:profile', kwargs={'pk': self.user.pk})
        )

    def test_login_router_without_profile(self):
        """Tests the router if the user does not have a profile"""
        # Create a new user without a Profile
        self.user_no_profile = get_user_model().objects.create_superuser(
            email='no@profile.com',
            username='no_profile',
            password='testpass'
        )
        self.client.login(username='no@profile.com', password='testpass')
        resp = self.client.get(reverse('profiles:login_router'))

        self.assertRedirects(resp, reverse('profiles:edit'))