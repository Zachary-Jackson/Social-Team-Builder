from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile, Skill, Project, Position


class ProfileViewsTests(TestCase):
    """This tests to see if profile's views work"""
    def setUp(self):
        """Creates a Profile and some skills for testing"""
        # Get the current User model
        # A Profile object will be added to this user
        user = get_user_model()
        self.user = user.objects.create_user(
            email='test@test.com',
            password='testpass'
        )

        # Create a new user without a Profile object
        self.user_no_profile = user.objects.create_user(
            email='no@profile.com',
            password='testpass'
        )

        # Creates a couple of Skill(s)
        self.skill_1 = Skill.objects.create(skill='Django')
        self.skill_2 = Skill.objects.create(skill='Angular')
        self.skill_3 = Skill.objects.create(skill='Mountain Climbing')

        # Creates a profile for a user without an avatar
        self.profile = Profile.objects.create(
            user=self.user,
            username='Santa',
            bio='The weather forecast shows snow for the next five months.',
        )
        self.profile.skills.add(self.skill_1, self.skill_2)

        # Creates a Position to attach to a Project
        self.position = Position.objects.create(
            skill=self.skill_1, information='this is the position', filled=False
        )

        # Creates a Project
        self.project = Project.objects.create(
            owner=self.profile, title='Team Builder',
            time_line='Depends on the number of features',
            requirements='See the README.md', description='also see README.md'
        )
        self.project.positions.add(self.position)

    def test_homepage(self):
        """Tests the homepage's content"""
        resp = self.client.get(reverse('profiles:homepage'))

        # projects that need field and their needs
        self.assertContains(resp, 'Team Builder')
        self.assertContains(resp, 'Django')
        # various page information
        self.assertContains(resp, 'Projects')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Projects')

    def test_login_router_with_profile(self):
        """Tests the router if the user has a profile"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(reverse('profiles:login_router'))
        self.assertRedirects(
            resp, reverse('profiles:profile', kwargs={'pk': self.profile.pk}))

    def test_login_router_without_profile(self):
        """Tests the router if the user does not have a profile"""
        self.client.login(username='no@profile.com', password='testpass')
        resp = self.client.get(reverse('profiles:login_router'))

        # Checks that a second Profile was created
        self.assertEqual(2, len(Profile.objects.all()))

        self.assertRedirects(resp, reverse('profiles:edit'))

    """Profile tests"""

    def test_profile_edit_not_logged_in(self):
        """Ensures that profile_edit requires log in"""
        # @login_required does this, but in case its deleted somehow
        resp = self.client.get(reverse('profiles:edit'))

        # The user has not logged in, so we should get redirected
        self.assertEqual(resp.status_code, 302)

    def test_profile_edit(self):
        """Ensures that profile_edit appears correctly"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(reverse('profiles:edit'))

        # our profile information
        self.assertContains(resp, 'Santa')
        self.assertContains(resp, 'The weather forecast shows snow for the')
        # various page information
        self.assertContains(resp, 'Applications')
        self.assertContains(resp, 'Past Projects')
        self.assertContains(resp, 'My Skills')
        self.assertContains(resp, 'Save Changes')
        self.assertContains(resp, 'Profile')

    def test_profile_edit_post(self):
        """Ensures that profile_edit can update the Profile"""
        self.client.login(username='test@test.com', password='testpass')
        self.client.post(
            reverse('profiles:edit'),
            data={'bio': 'new bio', 'username': 'editor'})

        # get the updated profile for testing
        profile = Profile.objects.get(pk = self.profile.pk)

        self.assertEqual(profile.bio, 'new bio')
        self.assertEqual(profile.username, 'editor')

    def test_profile_view(self):
        """Ensures the profile_view is working"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:profile', kwargs={'pk': self.profile.pk}))

        self.assertContains(resp, "Santa's profile")
        self.assertContains(resp, 'The weather forecast shows snow for')
        self.assertContains(resp, 'Past Projects')
        self.assertContains(resp, 'Edit')
        self.assertContains(resp, 'Django')
        self.assertContains(resp, 'Angular')
        # The edit button should appear to allow the logged in user to edit
        # their profile
        self.assertContains(resp, 'Edit')

    """Project tests"""

    def test_project_delete(self):
        """Ensures a user can delete a project"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:project_delete', kwargs={'pk': self.project.pk}))

        # Ensure that there is now zero Projects
        self.assertEqual(len(Project.objects.all()), 0)

    def test_project_delete_unowned(self):
        """Ensures only the project owner can delete a project"""
        self.client.login(username='no@profile.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:project_delete', kwargs={'pk': self.project.pk}))

        # Ensure that there is now zero Projects
        self.assertEqual(resp.status_code, 404)

    def test_project_delete_confirmation_post(self):
        """Ensures a user can go back to the edit page"""
        # This tests to see if a user can go back
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.post(
            reverse('profiles:project_delete_confirmation',
                    kwargs={'pk': self.project.pk}),
            data={'back': 'Go Back'}
        )
        self.assertRedirects(
            resp, reverse('profiles:project_edit',
                          kwargs={'pk': self.project.pk}))

    def test_project_delete_confirmation_unowned(self):
        """Ensures only the project owner can delete a project"""
        self.client.login(username='no@profile.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:project_delete_confirmation',
                    kwargs={'pk': self.project.pk}))

        # Ensure that there is now zero Projects
        self.assertEqual(resp.status_code, 404)


    def test_project_edit_not_logged_in(self):
        """We should be routed to the login page"""
        resp = self.client.get(
            reverse('profiles:project_edit', kwargs={'pk': self.project.pk}))
        self.assertEqual(resp.status_code, 302)

    def test_project_edit(self):
        """Ensures project_edit appears correctly"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:project_edit', kwargs={'pk': self.project.pk}))

        # project information
        self.assertContains(resp, 'Team Builder')
        self.assertContains(resp, 'Depends on the number of features')
        self.assertContains(resp, 'See the README.md')
        self.assertContains(resp, 'also see README.md')
        self.assertContains(resp, 'See the README.md')
        # page information
        self.assertContains(resp, 'Project Timeline')
        self.assertContains(resp, 'Save Changes')
        self.assertContains(resp, 'Delete Project')

    def test_project_edit_post(self):
        """Ensures project_edit appears correctly"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.post(
            reverse('profiles:project_edit', kwargs={'pk': self.project.pk}),
            data={
                'title': 'test post', 'time_line': 'milliseconds',
                'owner': self.user.pk,
                'requirements': 'data to post', 'description': 'description',
                'skill': self.skill_1.pk, 'information': 'This is a good skill'
            }
        )

        # Get the updated Project
        project = Project.objects.get(pk=self.project.pk)
        self.assertEqual(project.title, 'test post')
        self.assertEqual(project.time_line, 'milliseconds')
        self.assertEqual(project.requirements, 'data to post')
        self.assertEqual(project.description, 'description')

        self.assertRedirects(
            resp, reverse('profiles:project', kwargs={'pk': self.project.pk}))

    def test_project_edit_unowned(self):
        """Tests to make sure a logged in user can not edit other's Projects"""
        self.client.login(username='no@profile.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:project_edit', kwargs={'pk': self.project.pk}))

        # Ensure we were kicked out
        self.assertEqual(resp.status_code, 404)

    def test_project_new(self):
        """Ensures project_new looks correct."""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(reverse('profiles:project_new'))

        # page information
        self.assertContains(resp, 'Save Changes')
        self.assertContains(resp, 'Positions')
        self.assertContains(resp, 'Project Title')
        self.assertContains(resp, 'Application Requirements')

        self.assertNotContains(resp, 'Delete Project')

    def test_project_post(self):
        """Ensures a user can post a new project"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.post(
            reverse('profiles:project_new'),
            data={
                'title': 'Second Project', 'time_line': 'very small',
                'owner': self.user.pk,
                'requirements': 'data to post', 'description': 'description',
                'skill': self.skill_3.pk,
                'information': 'Maybe you are on the wrong site.'
            })

        # In addition to the project/position created in SetUp
        # we should have these two
        self.assertEqual(len(Project.objects.all()), 2)
        self.assertEqual(len(Position.objects.all()), 2)

        project_2 = Project.objects.get(pk=2)
        self.assertEqual(project_2.title, 'Second Project')
        self.assertEqual(project_2.description, 'description')

        position_2 = Position.objects.get(pk=2)
        self.assertEqual(
            position_2.information, 'Maybe you are on the wrong site.')

    def test_project_view_not_logged_in(self):
        """Ensures that the project view page is working"""
        resp = self.client.get(
            reverse('profiles:project', kwargs={'pk': self.project.pk}))

        self.assertEqual(resp.status_code, 200)

        # This checks that all the project pieces are on the website
        self.assertContains(resp, 'Team Builder')
        self.assertContains(resp, 'Depends on the number of features')
        self.assertContains(resp, 'See the README.md')
        self.assertContains(resp, 'also see README.md')
        # This is the position parts of the project
        self.assertContains(resp, 'this is the position')
        self.assertContains(resp, 'Django')

        # Because we are not logged in, the following should not appear
        self.assertNotContains(resp, 'Edit Project')
        self.assertNotContains(resp, 'Delete Project')

    def test_project_view(self):
        """Logged in test"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:project', kwargs={'pk': self.project.pk}))

        # Because we are logged in, the following should appear
        self.assertContains(resp, 'Edit Project')
        self.assertContains(resp, 'Delete Project')

    def test_project_view_bad_pk(self):
        """We should get a 404 error"""
        resp = self.client.get(
            reverse('profiles:project', kwargs={'pk': 10947}))
        self.assertEqual(resp.status_code, 404)