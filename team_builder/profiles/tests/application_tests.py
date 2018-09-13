from django.urls import reverse


from .base_tests import BaseTestWithPositionsProjects
from ..models import (Applicants, Position)


class ApplicationsTests(BaseTestWithPositionsProjects):
    """Tests all the views from applications_views"""

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

        self.assertTemplateUsed('applications.html')

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

        self.assertTemplateUsed('applicants_accepted.html')

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

        self.assertTemplateUsed('applicants_rejected.html')