from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile, Skill, Project, Position


class ProfileViewsTests(TestCase):
    """This tests to see if profile's views work"""
    def setUp(self):
        """Creates a Profile and some skills for testing"""
        # Get the current User model
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@test.com',
            password='verysecret1'
        )

        # Creates a couple of Skill(s)
        self.skill_1 = Skill.objects.create(skill='Django')
        self.skill_2 = Skill.objects.create(skill='Angular')
        self.skill_3 = Skill.objects.create(skill='Mountain Climbing')

        # Creates a profile for a user without an avatar
        self.profile = Profile.objects.create(
            user=self.user,
            username='Santa',
            bio='The weather forcast shows snow for the next five months.',
        )
        self.profile.skills.add(self.skill_1)

        # Creates a Position to attach to a Project
        self.position = Position.objects.create(
            skill=self.skill_1, information='this is the position', filled=False
        )

        # Creates a Project
        self.project = Project.objects.create(
            owner=self.profile, title='Team Builder',
            time_line='Depends on the number of features',
            requirements='See the README.md', description='also see README.MD'
        )
        self.project.positions.add(self.position)

    def test_profile_edit_not_logged_in(self):
        """Ensures that profile_edit requires log in"""
        resp = self.client.get(reverse('profiles:edit'))

        # The user has not logged in, so we should get redirected
        self.assertEqual(resp.status_code, 302)

    def test_project_view_not_logged_in(self):
        """Ensures that the project view page is working"""
        resp = self.client.get(
            reverse('profiles:project', kwargs={'pk': self.project.pk}))

        self.assertEqual(resp.status_code, 200)

        # This checks that all the project pieces are on the website
        self.assertContains(resp, 'Team Builder')
        self.assertContains(resp, 'Depends on the number of features')
        self.assertContains(resp, 'See the README.md')
        self.assertContains(resp, 'also see README.MD')
        # This is the position parts of the project
        self.assertContains(resp, 'this is the position')
        self.assertContains(resp, 'Django')

        # Because we are not logged in, the following should not appear
        self.assertNotContains(resp, 'Edit Project')
        self.assertNotContains(resp, 'Delete Project')

    def test_project_view_bad_pk(self):
        """We should get a 404 error"""
        resp = self.client.get(
            reverse('profiles:project', kwargs={'pk': 10947}))
        self.assertEqual(resp.status_code, 404)


    def test_project_edit_not_logged_in(self):
        """We should be routed to the login page"""
        resp = self.client.get(
            reverse('profiles:project_edit', kwargs={'pk': self.project.pk}))
        self.assertEqual(resp.status_code, 302)