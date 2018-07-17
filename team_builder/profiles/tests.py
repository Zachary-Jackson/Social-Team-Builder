from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# django-notifications-hq
from notifications.signals import notify

from .models import AllSkills, Applicants, Skill, Project, Position


class ProfileViewsTests(TestCase):
    """This tests to see if profile's views work"""
    def setUp(self):
        """Creates a Profile and some skills for testing"""

        # Creates a couple of Skill(s)
        self.skill_1 = Skill.objects.create(skill='Django developer')
        self.skill_2 = Skill.objects.create(skill='Angular')
        self.skill_3 = Skill.objects.create(skill='Mountain Climbing')

        # Get the current User model
        user = get_user_model()

        # Create the first user for testing
        self.user = user.objects.create_user(
            email='user@user.com',
            username='Santa',
            password='testpass'
        )
        self.user.bio = (
            'The weather forecast shows snow for the next five months.'
        )
        self.user.save()
        self.user_1_skills = AllSkills.objects.create(user_id=self.user.pk)
        self.user_1_skills.skills.add(self.skill_1, self.skill_2)

        # Creates a second user
        user = get_user_model()
        self.user_2 = user.objects.create_user(
            email='user2@user2.com',
            username='Hattie',
            password='testpass',
        )
        self.user_2.bio = 'I am a wild little dog.'
        self.user_2.save()
        self.user_2_skills = AllSkills.objects.create(user_id=self.user_2.pk)
        self.user_2_skills.skills.add(self.skill_1, self.skill_3)

        # Creates a Project
        self.project = Project.objects.create(
            owner=self.user, title='Test Project',
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
    #
    #     # The following is to create messages to test notifications
    #
    #     # Create a message to send to self.user
    #     skill = self.skill_1
    #     project = self.project
    #     self.message_1 = (
    #         f'You have been accepted as a {skill} for the project: {project}'
    #     )
    #
    #     # Accepted message unread
    #     notify.send(
    #         self.profile_2,
    #         recipient=self.user,
    #         verb=self.message_1
    #     )
    #
    #     # Declined message read
    #     self.message_2 = (
    #         f'You have been rejected as a {skill} for the project: {project}'
    #     )
    #
    #     notify.send(
    #         self.profile_2,
    #         recipient=self.user,
    #         verb=self.message_2
    #     )
    #     self.user.notifications.get(pk=2).mark_as_read()
    #
    """Miscellaneous test"""

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

        self.assertTemplateUsed('profiles/homepage.html')

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
        self.user_no_profile = get_user_model().objects.create_user(
            email='no@profile.com',
            username='no_profile',
            password='testpass'
        )
        self.client.login(username='no@profile.com', password='testpass')
        resp = self.client.get(reverse('profiles:login_router'))

        self.assertRedirects(resp, reverse('profiles:edit'))

    """Applications tests"""

    def test_applications(self):
        """Ensures the applications view works"""
        self.client.login(username='user@user.com', password='testpass')

        resp = self.client.get(reverse('profiles:applications'))

        # page information
        self.assertContains(resp, 'Applications')
        self.assertContains(resp, 'All Open Applications')
        self.assertContains(resp, 'Accepted')

        # There should be no found results
        self.assertContains(resp, 'You have no open positions')
        self.assertNotContains(resp, 'Hattie')
        # But we should have one open project
        self.assertContains(resp, 'Test Project')

    def test_applications_with_data(self):
        """Ensures that an applicant can be found"""
        self.client.login(username='user@user.com', password='testpass')

        # Create an applicant for self.project
        applicant = Applicants.objects.create(
            applicant=self.user_2,
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
        self.client.login(username='user@user.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:applications_accept',
                    kwargs={
                        'position_pk': self.position.pk,
                        'profile_pk': self.user_2.pk}
                    )
        )

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
        self.client.login(username='user@user.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:applications_reject',
                    kwargs={
                        'position_pk': self.position.pk,
                        'profile_pk': self.user_2.pk
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
        self.client.login(username='user@user.com', password='testpass')

        # Create an applicant for self.project
        applicant = Applicants.objects.create(
            applicant=self.user_2,
            position=self.position,
            accepted=True
        )

        # Add the applicant to the Position
        self.position.any_applicants = True
        self.position.filled_by = self.user_2
        self.filled = True
        self.position.applicants.add(applicant)
        self.position.save()

        resp = self.client.get(reverse('profiles:applications_view_accepted'))

        # Various page information
        self.assertContains(resp, 'Accepted Applicants')
        self.assertContains(resp, 'Filled Projects')
        self.assertContains(resp, 'Filled Needs')
        self.assertContains(resp, 'Django developer')

        # Ensure we get the second user's name
        self.assertContains(resp, 'Hattie')

        self.assertTemplateUsed('profiles/applicants_accepted.html')

    def test_applications_view_rejected_with_data(self):
        """Ensures that an accepted applicant can be found"""
        self.client.login(username='user@user.com', password='testpass')

        # Create an applicant for self.project
        applicant = Applicants.objects.create(
            applicant=self.user_2,
            position=self.position,
            rejected=True
        )

        # Add the applicant to the Position
        self.position.any_applicants = True
        self.position.filled_by = self.user_2
        self.filled = False
        self.position.applicants.add(applicant)
        self.position.save()

        resp = self.client.get(reverse('profiles:applications_view_rejected'))

        # Various page information
        self.assertContains(resp, 'Project Needs')
        self.assertContains(resp, 'Rejected Projects')
        self.assertContains(resp, 'Rejected Needs')
        self.assertContains(resp, 'Django developer')

        # Ensure we get the second user's name
        self.assertContains(resp, 'Hattie')

        self.assertTemplateUsed('profiles/applicants_rejected.html')

    # """Notification tests"""
    #
    # def test_notifications(self):
    #     """Ensures the main notifications view is working"""
    #     self.client.login(username='user@user.com', password='testpass')
    #
    #     resp = self.client.get(reverse('profiles:notifications'))
    #
    #     # various page information
    #     self.assertContains(resp, 'Notifications')
    #     self.assertContains(resp, 'Unread')
    #     self.assertContains(resp, 'Read')
    #     self.assertContains(resp, 'Deletion View')
    #     self.assertContains(resp, 'Time of notification')
    #     # notification information
    #     self.assertContains(resp, self.message_1)
    #     self.assertContains(resp, f'Unread from: {self.profile_2}')
    #     self.assertContains(resp, self.message_2)
    #     self.assertContains(resp, f'Read from: {self.profile_2}')
    #
    #     self.assertTemplateUsed('profiles/notifications.html')
    #
    # def test_notification_delete(self):
    #     """Ensures that a user can delete a notification"""
    #     self.client.login(username='user@user.com', password='testpass')
    #
    #     resp = self.client.get(
    #         reverse('profiles:notifications_delete',
    #                 kwargs={'pk': 1}))
    #
    #     self.assertEqual(len(self.user.notifications.all()), 1)
    #     self.assertRedirects(
    #         resp,
    #         reverse('profiles:notifications_deletion_view')
    #     )
    #
    # def test_notifications_deletion_view(self):
    #     """Ensures the read notifications view is working"""
    #     self.client.login(username='user@user.com', password='testpass')
    #
    #     resp = self.client.get(reverse('profiles:notifications_deletion_view'))
    #
    #     # various page information
    #     self.assertContains(resp, 'Notifications')
    #     self.assertContains(resp, 'Unread')
    #     self.assertContains(resp, 'Read')
    #     self.assertContains(resp, 'Deletion View')
    #     self.assertContains(resp, 'Read notifications for deletion')
    #     self.assertContains(resp, 'Time of notification')
    #     # notification information
    #     self.assertContains(resp, self.message_2)
    #     self.assertContains(resp, 'Delete')
    #     self.assertContains(resp, f'From: {self.profile_2}')
    #
    #     self.assertTemplateUsed('profiles/notifications_deletion.html')
    #
    # def test_notification_mark_read(self):
    #     """Ensures that a user can mark a notification as read"""
    #     self.client.login(username='user@user.com', password='testpass')
    #
    #     resp = self.client.get(
    #         reverse('profiles:notifications_mark_read',
    #                 kwargs={'pk': 1}))
    #
    #     # We should not have deleted a notification
    #     self.assertEqual(len(self.user.notifications.all()), 2)
    #     self.assertEqual(self.user.notifications.get(pk=1).unread, False)
    #
    #     self.assertRedirects(
    #         resp,
    #         reverse('profiles:notifications_unread')
    #     )
    #
    # def test_notification_mark_unread(self):
    #     """Ensures that a user can mark a notification as unread"""
    #     self.client.login(username='user@user.com', password='testpass')
    #
    #     resp = self.client.get(
    #         reverse('profiles:notifications_mark_unread',
    #                 kwargs={'pk': 2}))
    #
    #     # We should not have deleted a notification
    #     self.assertEqual(len(self.user.notifications.all()), 2)
    #     self.assertEqual(self.user.notifications.get(pk=2).unread, True)
    #
    #     self.assertRedirects(
    #         resp,
    #         reverse('profiles:notifications_read')
    #     )
    #
    # def test_notifications_read(self):
    #     """Ensures the read notifications view is working"""
    #     self.client.login(username='user@user.com', password='testpass')
    #
    #     resp = self.client.get(reverse('profiles:notifications_read'))
    #
    #     # various page information
    #     self.assertContains(resp, 'Notifications')
    #     self.assertContains(resp, 'Unread')
    #     self.assertContains(resp, 'Read')
    #     self.assertContains(resp, 'Deletion View')
    #     self.assertContains(resp, 'Read Notifications')
    #     self.assertContains(resp, 'Time of notification')
    #     # notification information
    #     self.assertContains(resp, self.message_2)
    #     self.assertContains(resp, 'Mark unread')
    #     self.assertContains(resp, f'From: {self.profile_2}')
    #
    #     self.assertTemplateUsed('profiles/notifications_read.html')
    #
    # def test_notifications_unread(self):
    #     """Ensures the unread notifications view is working"""
    #     self.client.login(username='user@user.com', password='testpass')
    #
    #     resp = self.client.get(reverse('profiles:notifications_unread'))
    #
    #     # various page information
    #     self.assertContains(resp, 'Notifications')
    #     self.assertContains(resp, 'Unread')
    #     self.assertContains(resp, 'Read')
    #     self.assertContains(resp, 'Deletion View')
    #     self.assertContains(resp, 'Unread Notifications')
    #     self.assertContains(resp, 'Time of notification')
    #     # notification information
    #     self.assertContains(resp, self.message_1)
    #     self.assertContains(resp, 'Mark read')
    #     self.assertContains(resp, f'From: {self.profile_2}')
    #
    #     self.assertTemplateUsed('profiles/notifications_unread.html')
    #
    """Profile view tests"""

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
        self.assertContains(resp, 'Past Projects')
        self.assertContains(resp, 'My Skills')
        self.assertContains(resp, 'Save Changes')
        self.assertContains(resp, 'Profile')
        self.assertContains(resp, 'Bio (markdown preview bellow)')

        # skills_form information
        self.assertContains(resp, str(self.skill_1))
        self.assertContains(resp, str(self.skill_2))
        self.assertContains(resp, str(self.skill_3))

        self.assertTemplateUsed('profiles/profile_edit.html')

    def test_profile_edit_post(self):
        """Ensures that profile_edit can update the Profile"""
        self.client.login(username='user@user.com', password='testpass')
        self.client.post(
            reverse('profiles:edit'),
            data={'bio': 'new bio', 'username': 'editor'})

        # get the updated profile for testing
        user_model = get_user_model()
        profile = user_model.objects.get(pk=self.user.pk)

        self.assertEqual(profile.bio, 'new bio')
        self.assertEqual(profile.username, 'editor')

        self.assertTemplateUsed('profiles/profile_edit.html')

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
        self.assertContains(resp, str(self.skill_1))
        # The edit button should appear to allow the logged in user to edit
        # their profile
        self.assertContains(resp, 'Edit')

        self.assertTemplateUsed('profiles/profile.html')

    """Project tests"""

    def test_project_delete(self):
        """Ensures a user can delete a project"""
        self.client.login(username='user@user.com', password='testpass')
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
        self.client.login(username='user@user.com', password='testpass')
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
        self.client.login(username='user@user.com', password='testpass')
        resp = self.client.get(
            reverse('profiles:project_edit', kwargs={'pk': self.project.pk}))

        # project information
        self.assertContains(resp, 'Test Project')
        self.assertContains(resp, 'Depends on the number of features')
        self.assertContains(resp, 'See the README.md')
        self.assertContains(resp, 'also see README.md')
        self.assertContains(resp, 'See the README.md')
        self.assertContains(resp, 'Description (markdown preview bellow)')
        # page information
        self.assertContains(resp, 'Project Timeline')
        self.assertContains(resp, 'Save Changes')
        self.assertContains(resp, 'Delete Project')

        self.assertTemplateNotUsed('profiles/project_edit.html')

    def test_project_edit_post(self):
        """Ensures project_edit appears correctly"""
        self.client.login(username='user@user.com', password='testpass')
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
        self.client.login(username='user@user.com', password='testpass')
        resp = self.client.get(reverse('profiles:project_new'))

        # page information
        self.assertContains(resp, 'Save Changes')
        self.assertContains(resp, 'Positions')
        self.assertContains(resp, 'Project Title')
        self.assertContains(resp, 'Application Requirements')
        self.assertContains(resp, 'Description (markdown preview bellow)')

        # You can not delete a project that does not exist
        self.assertNotContains(resp, 'Delete Project')

        self.assertTemplateNotUsed('profiles/project_edit.html')

    def test_project_new_post(self):
        """Ensures a user can post a new project"""
        self.client.login(username='user@user.com', password='testpass')
        self.client.post(
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
        self.assertContains(resp, 'Test Project')
        self.assertContains(resp, 'Depends on the number of features')
        self.assertContains(resp, 'See the README.md')
        self.assertContains(resp, 'also see README.md')
        # This is the position parts of the project
        self.assertContains(resp, 'this is the position')
        self.assertContains(resp, 'Django developer')

        # Because we are not logged in, the following should not appear
        self.assertNotContains(resp, 'Edit Project')
        self.assertNotContains(resp, 'Delete Project')

        self.assertTemplateNotUsed('profiles/project.html')

    def test_project_view(self):
        """Logged in test"""
        self.client.login(username='user@user.com', password='testpass')
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
        self.client.login(username='user@user.com', password='testpass')
        resp = self.client.get(reverse('profiles:project_view_all'))

        # Page Information
        self.assertContains(resp, 'My Projects')
        self.assertContains(resp, 'Applications')
        self.assertContains(resp, 'All Positions')
        # Project information
        self.assertContains(resp, 'Test Project')
        self.assertContains(resp, 'Django developer')

        self.assertTemplateUsed('profiles/project_view_all.html')

    """Searching tests"""

    def test_search(self):
        """Ensures that a user can search for projects"""
        resp = self.client.get(
            reverse('profiles:search'),
            # search with a lowercase search term
            data={'search_term': 'Test Project'})

        # projects that matches the search term "Test Project"
        self.assertContains(resp, 'Test Project')
        self.assertContains(resp, 'Django developer')
        # various page information
        self.assertContains(resp, 'Projects')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Projects')

        self.assertTemplateUsed('profiles:homepage.html')

    def test_search_by_skill(self):
        """Ensures that a user can search projects via skill"""
        resp = self.client.get(
            reverse('profiles:search_by_skill',
                    kwargs={'skill': 'Django developer'}))

        # projects that matches the search term Django developer
        self.assertContains(resp, 'Test Project')
        self.assertContains(resp, '1 results were found with: Django developer')
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

    def test_search_your_skills(self):
        """Checks that all projects are found with your skills"""
        self.client.login(username='user2@user2.com', password='testpass')

        resp = self.client.get(reverse('profiles:search_your_skills'))

        # self.user2 has a profile with the Django developer skill
        # self.project has one open position for Django developer, so
        # we should find one result
        self.assertContains(
            resp,
            '1 results were found with: Your Skills')

        # various page information
        self.assertContains(resp, 'Test Project')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Projects')

        self.assertTemplateUsed('profiles:homepage.html')