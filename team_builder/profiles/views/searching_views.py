from operator import attrgetter

from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import ListView

from .. import models


def create_search_result_string(projects, search_term):
    """Creates a formatted string stating what results were found"""
    if not projects:
        search_results = 'No results were found with: {}'.format(search_term)
    else:
        search_results = '{} results were found with: {}'.format(
            len(projects), search_term)
    return search_results


class SearchViewMixin(object):
    """Creates a template for the Search views
    This sets the model and template_name as well as the skills context"""
    model = models.Project
    template_name = 'profiles/homepage.html'

    def get_context_data(self, **kwargs):
        context = super(SearchViewMixin, self).get_context_data(**kwargs)
        context['skills'] = (
            sorted(models.Skill.objects.all(), key=attrgetter('skill'))
        )
        return context


"""searching related views"""


class SearchListView(SearchViewMixin, ListView):
    """Searches all projects and returns the results"""

    def get_context_data(self, *, object_list=None, **kwargs):
        """"Gets all skills from the database and the search_results string"""
        context = super(SearchListView, self).get_context_data(**kwargs)

        search_term = self.request.GET.get('search_term')
        if not search_term:
            return redirect('profiles:homepage')
        context['search_results'] = (
            create_search_result_string(self.get_queryset(), search_term)
        )
        return context

    def get_queryset(self):
        """Filters all fields for all projects by the search term"""
        search_term = self.request.GET.get('search_term')
        if not search_term:
            return redirect('profiles:homepage')

        return models.Project.objects.filter(positions__filled=False)\
            .prefetch_related('positions')\
            .filter(
                Q(title__icontains=search_term) |
                Q(time_line__icontains=search_term) |
                Q(requirements__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(positions__information__icontains=search_term)
        ).distinct()


class SearchBySkillListView(SearchViewMixin, ListView):
    """Searches projects by skills needed"""

    def get_context_data(self, *, object_list=None, **kwargs):
        """"Gets all skills from the database and the search_results string"""
        context = super(SearchBySkillListView, self).get_context_data(**kwargs)

        # The skill might be in a url acceptable format without spaces
        # if so we need to remove the spaces
        # See Skill's readable_to_url method
        skill = self.kwargs['skill'].replace('_', ' ')
        context['search_results'] = (
            create_search_result_string(self.get_queryset(), skill)
        )

        # if the searched skill is not a Skill, don't create a
        # 'skill_selector' context
        try:
            found_skill = models.Skill.objects.get(skill=skill)
            context['skill_selector'] = found_skill
        except models.Skill.DoesNotExist:
            pass

        return context

    def get_queryset(self):
        """Filters all fields for all projects by the search term"""
        # See above get_context_data
        skill = self.kwargs['skill'].replace('_', ' ')

        return models.Project.objects.filter(
            Q(
                positions__skill__skill__contains=skill,
                positions__filled=False,
            )
        ).prefetch_related('positions__skill').distinct()


class SearchYourSkillsView(SearchViewMixin, ListView):
    """Finds all of the projects that needs the user's skills"""
    login_required = True

    def get_context_data(self, *, object_list=None, **kwargs):
        """"Gets all skills from the database and the search_results string"""
        context = super(SearchYourSkillsView, self).get_context_data(**kwargs)

        context['skill_selector'] = 'Your Projects'
        context['search_results'] = (
            create_search_result_string(self.get_queryset(), 'Your Skills')
        )

        return context

    def get_queryset(self):
        """Filters all fields for all projects by the search term"""
        # The user's skills
        skills = self.request.user.allskills.skills.all()

        # Get all of the projects
        all_projects = models.Project.objects\
            .filter(positions__filled=False).distinct()

        # Create a list to add all the found projects to
        found_projects = set()

        for skill in skills:
            query = all_projects.filter(
                Q(positions__skill__skill__contains=skill))
            # If the query is empty, do not add to found_projects
            if len(query):
                found_projects.add(query)

        projects = []
        for queryset in found_projects:
            for query in queryset:
                projects.append(query)

        return projects
