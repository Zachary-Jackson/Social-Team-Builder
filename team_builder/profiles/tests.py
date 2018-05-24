from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile, Skill


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

    def test_profile_view_not_logged_in(self):
        """Ensures that profile_view requires log in"""
        resp = self.client.get(reverse('profiles:edit'))

        # The user has not logged in, so we should get redirected
        self.assertEqual(resp.status_code, 302)
