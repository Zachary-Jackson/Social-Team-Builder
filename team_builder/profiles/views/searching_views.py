from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render

from .. import models


"""searching related views"""


def create_search_result_string(projects, search_term):
    """Creates a formatted string stating what results were found"""
    if not projects:
        search_results = 'No results were found with: {}'.format(search_term)
    else:
        search_results = '{} results were found with: {}'.format(
            len(projects), search_term)
    return search_results


def search(request):
    """Searches all projects and returns the results"""
    search_term = request.GET.get('search_term')

    # If no search term is provided reroute to homepage
    if not search_term:
        return redirect('profiles:homepage')

    projects = models.Project.objects.all().prefetch_related('positions')\
        .filter(
            Q(title__icontains=search_term) |
            Q(time_line__icontains=search_term) |
            Q(requirements__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(positions__information__icontains=search_term)
    ).distinct()

    # Various template things
    # Gets the search_results string
    search_results = create_search_result_string(projects, search_term)
    skills = sorted(models.Skill.objects.all(), key=attrgetter('skill'))

    return render(
        request,
        'profiles/homepage.html',
        {
            'projects': projects,
            'skills': skills,
            'search_results': search_results}
    )


def search_by_skill(request, skill):
    """Searches projects by skills needed"""
    # The skill might be in a url acceptable format without spaces
    # if so we need to remove the spaces
    # See Skill's readable_to_url method
    skill = skill.replace('_', ' ')

    skills = models.Skill.objects.all()

    # If the searched skill is not in skills, return no results
    try:
        found_skill = skills.get(skill=skill)
    except models.Skill.DoesNotExist:

        # Various template things
        # Creates the search_results string
        search_results = create_search_result_string(False, skill)
        sorted_skills = sorted(skills, key=attrgetter('skill'))
        return render(request, 'profiles/homepage.html',
                      {'search_results': search_results,
                       'skills': sorted_skills})

    # Get all projects that need a position with the searched skill
    projects = models.Project.objects.all().filter(
        Q(positions__skill__skill__contains=skill))\
        .prefetch_related('positions__skill').distinct()

    # Various template things
    # Creates the search_results string
    search_results = create_search_result_string(projects, skill)
    sorted_skills = sorted(skills, key=attrgetter('skill'))

    return render(request, 'profiles/homepage.html',
                  {'projects': projects,
                   'search_results': search_results,
                   'skill_selector': found_skill,
                   'skills': sorted_skills})


@login_required
def search_your_skills(request):
    """Finds all of the projects that needs the user's skills"""
    skills = request.user.profile.skills.all()

    # Creates the sorted_skills for the template
    all_skills = models.Skill.objects.all()
    sorted_skills = sorted(all_skills, key=attrgetter('skill'))

    # Get all of the projects
    all_projects = models.Project.objects.all()

    # Create a list to add all the found projects to
    found_projects = set()

    for skill in skills:
        found_projects.add(
            all_projects.filter(
                Q(positions__skill__skill__contains=skill)
            ))

    projects = []
    for queryset in found_projects:
        for query in queryset:
            projects.append(query)

    # Get all of the information for the template
    search_results = create_search_result_string(found_projects, 'Your Skills')
    skill_selector = 'Your Projects'

    return render(request, 'profiles/homepage.html',
                  {'projects': projects,
                   'search_results': search_results,
                   'skill_selector': skill_selector,
                   'skills': sorted_skills})