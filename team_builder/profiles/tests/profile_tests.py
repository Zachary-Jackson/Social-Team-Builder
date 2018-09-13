from django.urls import reverse

from .base_tests import BaseTestWithPositionsProjects


class ProfileTests(BaseTestWithPositionsProjects):
    """Tests all the views from profile_views"""

    def test_profile_edit_not_logged_in(self):
        """Ensures that profile_edit requires log in"""
        # @login_required does this, but in case its deleted somehow
        resp = self.client.get(reverse('profiles:edit'))

        # The user has not logged in, so we should get redirected
        self.assertEqual(resp.status_code, 302)

        self.assertTemplateNotUsed('profiles/profile_edit.html')

    def test_profile_edit(self):
        """Ensures that profile_edit appears correctly"""
        self.client.login(username='user@user.com', password='testpass')
        resp = self.client.get(reverse('profiles:edit'))

        # our profile information
        self.assertContains(resp, 'Santa')
        self.assertContains(resp, 'The weather forecast shows snow for the')
        # various page information
        self.assertContains(resp, 'Applications')
        self.assertContains(resp, 'My Skills')
        self.assertContains(resp, 'Save Changes')
        self.assertContains(resp, 'Profile')
        self.assertContains(resp, 'Bio (markdown preview bellow)')

        # skills_form information
        self.assertContains(resp, str(self.skill_1))
        self.assertContains(resp, str(self.skill_2))
        self.assertContains(resp, str(self.skill_3))

        self.assertTemplateUsed('profile_edit.html')

    def test_profile_view(self):
        """Ensures the profile_view is working"""
        self.client.login(username='user@user.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:profile', kwargs={'pk': self.user.pk}))

        self.assertContains(resp, "Santa's profile")
        self.assertContains(resp, 'The weather forecast shows snow for')
        self.assertContains(resp, 'Past Projects')
        self.assertContains(resp, 'Edit')
        self.assertContains(resp, 'Django developer')
        self.assertContains(resp, 'Angular')
        self.assertContains(resp, 'Image editor')
        self.assertContains(resp, str(self.skill_1))
        # The edit button should appear to allow the logged in user to edit
        # their profile
        self.assertContains(resp, 'Edit')

        self.assertTemplateUsed('profile.html')