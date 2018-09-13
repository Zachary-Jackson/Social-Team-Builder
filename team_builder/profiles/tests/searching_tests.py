from django.urls import reverse

from .base_tests import BaseTestWithPositionsProjects


class SearchingTests(BaseTestWithPositionsProjects):
    """Tests all the views from searching_views"""

    def test_search(self):
        """Ensures that a user can search for projects"""
        resp = self.client.get(
            reverse('profiles:search'),
            # search with a lowercase search term
            data={'search_term': 'Test Project'})

        # projects that matches the search term "Test Project"
        self.assertContains(resp, 'Test Project')
        self.assertContains(resp, 'Django developer')
        self.assertContains(resp, str(self.project))
        # various page information
        self.assertContains(resp, 'Projects')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Projects')

        self.assertTemplateUsed('homepage.html')

    def test_search_by_skill(self):
        """Ensures that a user can search projects via skill"""
        resp = self.client.get(
            reverse('profiles:search_by_skill',
                    kwargs={'skill': 'Django developer'}))

        # projects that matches the search term Django developer
        self.assertContains(resp, 'Test Project')
        self.assertContains(
            resp, '1 results were found with: Django developer'
        )
        self.assertContains(resp, str(self.project))
        # various page information
        self.assertContains(resp, 'Projects')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Projects')

        self.assertTemplateUsed('homepage.html')

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

        self.assertTemplateUsed('homepage.html')

    def test_search_your_skills(self):
        """Checks that all projects are found with your skills"""
        self.client.login(username='user2@user2.com', password='testpass')

        resp = self.client.get(reverse('profiles:search_your_skills'))

        # self.user2 has a profile with the Django developer skill
        # self.project has one open position for Django developer, so
        # we should find one result
        self.assertContains(
            resp,
            '1 results were found with: Your Skills'
        )
        self.assertContains(resp, str(self.project))

        # various page information
        self.assertContains(resp, 'Test Project')
        self.assertContains(resp, 'All Needs')
        self.assertContains(resp, 'Projects')

        self.assertTemplateUsed('homepage.html')