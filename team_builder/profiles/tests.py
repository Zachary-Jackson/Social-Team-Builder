from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Applicants, Profile, Skill, Project, Position


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

        # Creates a second user
        # A Profile object will be added to this user
        user = get_user_model()
        self.user_2 = user.objects.create_user(
            email='user2@user2.com',
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

        # Creates a profile for the second user
        self.profile_2 = Profile.objects.create(
            user=self.user_2,
            username='Hattie',
            bio='I am a wild little dog.',
        )

        self.profile_2.skills.add(self.skill_1, self.skill_3)

        # Creates a Project
        self.project = Project.objects.create(
            owner=self.profile, title='Team Builder',
            time_line='Depends on the number of features',
            requirements='See the README.md', description='also see README.md'
        )

        # Creates a Position to attach to a Project
        self.position = Position.objects.create(
            skill=self.skill_1, information='this is the position',
            related_project=self.project
        )

        # add a position to the main project
        self.project.positions.add(self.position)

    """Miscellaneous test"""

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

        self.assertTemplateUsed('profiles/homepage.html')

    def test_login_router_with_profile(self):
        """Tests the router if the user has a profile"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(reverse('profiles:login_router'))
        self.assertRedirects(
            resp, reverse('profiles:profile', kwargs={'pk': self.profile.pk})
        )

    def test_login_router_without_profile(self):
        """Tests the router if the user does not have a profile"""
        self.client.login(username='no@profile.com', password='testpass')
        resp = self.client.get(reverse('profiles:login_router'))

        # Checks that a third Profile was created
        self.assertEqual(3, len(Profile.objects.all()))

        self.assertRedirects(resp, reverse('profiles:edit'))

    """Applications tests"""

    def test_applications(self):
        """Ensures the applications view works"""
        self.client.login(username='test@test.com', password='testpass')

        resp = self.client.get(reverse('profiles:applications'))

        # page information
        self.assertContains(resp, 'Applications')
        self.assertContains(resp, 'All Open Applications')
        self.assertContains(resp, 'Accepted')

        # There should be no found results
        self.assertContains(resp, 'You have no open positions')
        self.assertNotContains(resp, 'Hattie')
        # But we should have one open project
        self.assertContains(resp, 'Team Builder')

    def test_applications_with_data(self):
        """Ensures that an applicant can be found"""
        self.client.login(username='test@test.com', password='testpass')

        # Create an applicant for self.project
        applicant = Applicants.objects.create(
            applicant=self.user_2.profile,
            position=self.position,
        )

        # Add the applicant to the Position
        self.position.any_applicants = True
        self.position.applicants.add(applicant)
        self.position.save()

        resp = self.client.get(reverse('profiles:applications'))

        # Ensure we get the second user's name
        self.assertContains(resp, 'Hattie')
        # We should be able to accept or reject this applicant.
        self.assertContains(resp, 'Accept')
        self.assertContains(resp, 'Reject')

        self.assertTemplateUsed('profiles/applications.html')

    def test_applications_accept(self):
        """Ensures a user can accept an application"""
        # Create an application for self.project from self.user_2
        self.client.login(username='user2@user2.com', password='testpass')
        self.client.get(
            reverse('profiles:applications_request',
                    kwargs={'pk': self.project.pk}))

        # Now that we have an applicant accept that application
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:applications_accept',
                    kwargs={
                        'position_pk': self.position.pk,
                        'profile_pk': self.user_2.profile.pk
            }
        ))

        # Ensure the applicant was updated properly
        applicant = Applicants.objects.get(pk=1)
        self.assertEqual(True, applicant.accepted)
        self.assertEqual(False, applicant.rejected)

        # Ensure the Position was updated properly
        position = Position.objects.get(pk=self.position.pk)
        self.assertEqual(True, position.filled)
        self.assertEqual(position.filled_by, applicant.applicant)

        # We should have been rerouted back to the main applications page
        self.assertRedirects(
            resp, reverse('profiles:applications'))

    def test_applications_rejected(self):
        """Ensures a user can reject an application"""
        # Create an application for self.project from self.user_2
        self.client.login(username='user2@user2.com', password='testpass')
        self.client.get(
            reverse('profiles:applications_request',
                    kwargs={'pk': self.project.pk}))

        # Now that we have an applicant accept that application
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:applications_reject',
                    kwargs={
                        'position_pk': self.position.pk,
                        'profile_pk': self.user_2.profile.pk
            }
        ))

        # Ensure the applicant was updated properly
        applicant = Applicants.objects.get(pk=1)
        self.assertEqual(False, applicant.accepted)
        self.assertEqual(True, applicant.rejected)

        # Ensure the Position was updated properly
        position = Position.objects.get(pk=self.position.pk)
        self.assertEqual(False, position.filled)

        # We should have been rerouted back to the main applications page
        self.assertRedirects(
            resp, reverse('profiles:applications'))

    def test_applications_request(self):
        """Ensures a user can submit an application request"""
        self.client.login(username='user2@user2.com', password='testpass')

        # There should be no applications
        self.assertEqual(0, len(Applicants.objects.all()))

        resp = self.client.get(
            reverse('profiles:applications_request',
                    kwargs={'pk': self.project.pk}))

        # We should have one application
        self.assertEqual(1, len(Applicants.objects.all()))

        # We should have been rerouted back to the project
        self.assertRedirects(
            resp, reverse('profiles:project',
                          kwargs={'pk': self.project.pk}))


    def test_applications_view_accepted_with_data(self):
        """Ensures that an accepted applicant can be found"""
        self.client.login(username='test@test.com', password='testpass')

        # Create an applicant for self.project
        applicant = Applicants.objects.create(
            applicant=self.user_2.profile,
            position=self.position,
            accepted=True
        )

        # Add the applicant to the Position
        self.position.any_applicants = True
        self.position.filled_by = self.user_2.profile
        self.filled = True
        self.position.applicants.add(applicant)
        self.position.save()

        resp = self.client.get(reverse('profiles:applications_view_accepted'))

        # Various page information
        self.assertContains(resp, 'Accepted Applicants')
        self.assertContains(resp, 'Filled Projects')
        self.assertContains(resp, 'Filled Needs')
        self.assertContains(resp, 'Django')

        # Ensure we get the second user's name
        self.assertContains(resp, 'Hattie')

        self.assertTemplateUsed('profiles/applicants_accepted.html')

    def test_applications_view_rejected_with_data(self):
        """Ensures that an accepted applicant can be found"""
        self.client.login(username='test@test.com', password='testpass')

        # Create an applicant for self.project
        applicant = Applicants.objects.create(
            applicant=self.user_2.profile,
            position=self.position,
            rejected=True
        )

        # Add the applicant to the Position
        self.position.any_applicants = True
        self.position.filled_by = self.user_2.profile
        self.filled = False
        self.position.applicants.add(applicant)
        self.position.save()

        resp = self.client.get(reverse('profiles:applications_view_rejected'))

        # Various page information
        self.assertContains(resp, 'Rejected Applicants')
        self.assertContains(resp, 'Rejected Projects')
        self.assertContains(resp, 'Rejected Needs')
        self.assertContains(resp, 'Django')

        # Ensure we get the second user's name
        self.assertContains(resp, 'Hattie')

        self.assertTemplateUsed('profiles/applicants_rejected.html')

    """Profile tests"""

    def test_profile_edit_not_logged_in(self):
        """Ensures that profile_edit requires log in"""
        # @login_required does this, but in case its deleted somehow
        resp = self.client.get(reverse('profiles:edit'))

        # The user has not logged in, so we should get redirected
        self.assertEqual(resp.status_code, 302)

        self.assertTemplateNotUsed('profiles/profile_edit.html')

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

        self.assertTemplateUsed('profiles/profile_edit.html')

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

        self.assertTemplateUsed('profiles/profile_edit.html')

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

        self.assertTemplateUsed('profiles/profile.html')

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
        self.client.login(username='user2@user2.com', password='testpass')
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

        self.assertTemplateUsed('profiles/project_delete_confirmation.html')

    def test_project_delete_confirmation_unowned(self):
        """Ensures only the project owner can delete a project"""
        self.client.login(username='user2@user2.com', password='testpass')
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

        self.assertTemplateNotUsed('profiles/project_edit.html')

    def test_project_edit_post(self):
        """Ensures project_edit appears correctly"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.post(
            reverse('profiles:project_edit', kwargs={'pk': self.project.pk}),
            data={
                'title': 'test post', 'time_line': 'milliseconds',
                'owner': self.user.pk,
                'requirements': 'data to post', 'description': 'description',
                # The following line is for the Position
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
        self.client.login(username='user2@user2.com', password='testpass')
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

        # You can not delete a project that does not exist
        self.assertNotContains(resp, 'Delete Project')

        self.assertTemplateNotUsed('profiles/project_edit.html')

    def test_project_new_post(self):
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

        self.assertTemplateNotUsed('profiles/project.html')

    def test_project_view(self):
        """Logged in test"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:project', kwargs={'pk': self.project.pk}))

        # Because we are logged in, the following should appear
        self.assertContains(resp, 'Edit Project')

    def test_project_view_bad_pk(self):
        """We should get a 404 error"""
        resp = self.client.get(
            reverse('profiles:project', kwargs={'pk': 10947}))
        self.assertEqual(resp.status_code, 404)

    def test_project_view_all(self):
        """Ensures the user can see all of their projects"""
        self.client.login(username='test@test.com', password='testpass')
        resp = self.client.get(reverse('profiles:project_view_all'))

        # Page Information
        self.assertContains(resp, 'My Projects')
        self.assertContains(resp, 'Applications')
        self.assertContains(resp, 'All Positions')
        # Project information
        self.assertContains(resp, 'Team Builder')
        self.assertContains(resp, 'Django')

        self.assertTemplateUsed('profiles/project_view_all.html')

    """Searching tests"""

    def test_search(self):
        """Ensures that a user can search for projects"""
        resp = self.client.get(
            reverse('profiles:search'),
            # search with a lowercase search term
            data={'search_term': 'team builder'})

        # projects that matches the search term "team builder"
        self.assertContains(resp, 'Team Builder')
        self.assertContains(resp, 'Django')
        # various page information
        self.assertContains(resp, 'Projects')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Projects')

        self.assertTemplateUsed('profiles:homepage.html')

    def test_search_by_skill(self):
        """Ensures that a user can search projects via skill"""
        resp = self.client.get(
            reverse('profiles:search_by_skill',
                    kwargs={'skill': 'Django'}))

        # projects that matches the search term Django
        self.assertContains(resp, 'Team Builder')
        self.assertContains(resp, '1 results were found with: Django')
        # various page information
        self.assertContains(resp, 'Projects')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Projects')

        self.assertTemplateUsed('profiles:homepage.html')

    def test_search_by_skill_invalid(self):
        """Ensures that an invalid search informs the user"""
        resp = self.client.get(
            reverse('profiles:search_by_skill',
                    kwargs={'skill': 'bad_search'}))

        # verify that the project informs the user to no results
        self.assertContains(
            resp,
            'No results were found with: bad search')

        # various page information
        self.assertContains(resp, 'Projects')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Projects')

        self.assertTemplateUsed('profiles:homepage.html')