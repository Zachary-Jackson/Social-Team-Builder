from django.urls import reverse

from .base_tests import BaseTestWithPositionsProjects
from ..models import Project


class ProjectTests(BaseTestWithPositionsProjects):
    """Tests all the views from project_views"""

    def test_project_delete(self):
        """Ensures a user can delete a project"""
        self.client.login(username='user@user.com', password='testpass')
        self.client.get(
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

        self.assertTemplateUsed('project_delete_confirmation.html')

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

        self.assertTemplateUsed('project_view_all.html')