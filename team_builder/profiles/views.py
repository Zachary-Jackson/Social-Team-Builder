from operator import attrgetter

from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from . import forms
from . import models


"""Miscellaneous views"""


def homepage(request):
    """This is the homepage for the profiles app"""
    projects = models.Project.objects.all().prefetch_related(
        'positions__skill')
    skills = sorted(models.Skill.objects.all(), key=attrgetter('skill'))

    return render(
        request,
        'profiles/homepage.html',
        {'skills': skills, 'projects': projects})


@login_required
def login_router(request):
    """Check to see if a Profile has been created.
    If not create and redirect to edit page"""
    try:
        request.user.profile
    except AttributeError:
        # create a Profile and redirect the user to the edit page
        models.Profile(user=request.user, username=request.user.email).save()
        return redirect('profiles:edit')
    else:
        # redirect to main profile page
        return redirect('profiles:profile', pk=request.user.profile.pk)


"""applications related views"""


def get_applicant(position, profile_pk: int):
    """Checks to see if an applicant is in a position if not 404
    Returns the found_applicant or 404"""
    # Get and update the Applicants model
    found_applicant = ''

    for applicant in position.applicants.all():
        if applicant.applicant.pk == profile_pk:
            found_applicant = applicant
            break

    # If an applicant is not found, 404
    if not found_applicant:
        raise Http404("An applicant was not found.")

    return found_applicant


def get_projects_with_filled_or_unfilled_positions(is_filled: bool, request):
    """Searches all of the User's projects and checks if they have
    filled or unfilled positions in them

    Returns found projects"""
    projects = models.Project.objects.all().filter(
        Q(owner=request.user.profile) & Q(positions__filled=is_filled))
    return projects


def get_needed_skills_and_found_positions(
        request, is_accepted: bool, is_filled: bool):
    """Gets all of the User's Positions
    Finds all of the applicants using is_filled

    returns the found_skills and needed_positions"""
    # Get all of the desired skills for the projects
    found_positions = set()
    needed_skills = set()

    positions = models.Position.objects.all()\
        .filter(position_creator=request.user.profile)

    for position in positions:

        if position.any_applicants and position.filled == is_filled:
            for applicant in position.applicants.all():
                
                if applicant.accepted == is_accepted and \
                        not applicant.rejected:
                    found_positions.add(applicant)
                    needed_skills.add(position.skill)

    return found_positions, needed_skills


@login_required
def applications(request):
    """This is the main applications page"""
    # Get projects that have all positions unfilled
    projects = get_projects_with_filled_or_unfilled_positions(False, request)

    # Get found_positions and needed_skills where the position is not filled
    found_positions, needed_skills = get_needed_skills_and_found_positions(
        request, is_accepted=False, is_filled=False
    )

    return render(
        request,
        'profiles/applications.html',
        {
            'applications_tab': 'All',
            'found_positions': found_positions,
            'current_tab': 'Applications',  # navigation bar selector
            'needed_skills': list(needed_skills),
            'projects': projects
        })


@login_required
def applications_accept(request, position_pk, profile_pk):
    """Allows the owner of a project to accept an applicant"""
    # if the current user does not own the project kick them out
    user = request.user.profile
    position = get_object_or_404(models.Position, pk=position_pk)
    profile = get_object_or_404(models.Profile, pk=profile_pk)

    if user != position.position_creator:
        raise Http404("You do not own this project")

    # Find the applicant or 404
    found_applicant = get_applicant(position, profile_pk)

    # Update the Applicant object
    found_applicant.accepted = True
    found_applicant.save()

    # Update the Position object
    position.filled_by = profile
    position.save()

    return redirect('profiles:applications')


@login_required
def applications_reject(request, position_pk, profile_pk):
    """Allows the owner of a project to reject an applicant

    Redirects to main applications page"""
    # if the current user does not own the project kick them out
    user = request.user.profile
    position = get_object_or_404(models.Position, pk=position_pk)
    get_object_or_404(models.Profile, pk=profile_pk)

    if user != position.position_creator:
        raise Http404("You do not own this project")

    # Find the applicant or 404
    found_applicant = get_applicant(position, profile_pk)

    # Update the Applicant object
    found_applicant.accepted = False
    found_applicant.rejected = True
    found_applicant.save()

    return redirect('profiles:applications')


@login_required
def applications_request(request, pk):
    """Allows a user to submit an application request"""
    # Ensures that the Position model exists or 404
    position = get_object_or_404(models.Position, pk=pk)
    user = request.user.profile

    # If the user has already applied, prevent another application
    for applicant in position.applicants.all():
        if applicant.applicant == user:
            raise Http404("You can only apply once.")

    # Create an Applicant model
    applicant = models.Applicants.objects.create(
        applicant=user,
        position=position

    )

    # Attach the applicant to a Position
    position.applicants.add(applicant)
    position.any_applicants = True
    position.save()

    # Return the user back to the Project's page
    return redirect('profiles:project', pk=pk)


@login_required
def applications_view_accepted(request):
    """Shows the user all of the applicants they have accepted"""
    # Get projects that have all positions filled
    projects = get_projects_with_filled_or_unfilled_positions(True, request)

    # Get found_positions and needed_skills where the position is filled
    found_positions, needed_skills = get_needed_skills_and_found_positions(
        request, is_accepted=True, is_filled=True
    )

    return render(
        request,
        'profiles/accepted_applicants.html',
        {
            'applications_tab': 'Accepted',
            'found_positions': found_positions,
            'current_tab': 'Applications',  # navigation bar selector
            'needed_skills': list(needed_skills),
            'projects': projects
        })


@login_required
def applications_view_rejected(request):
    """Shows the user all of the applicants they have rejected"""
    projects = []

    # Get all of the desired skills for the projects
    found_positions = set()
    needed_skills = set()

    # Get all of a user's positions
    positions = models.Position.objects.all()\
        .filter(position_creator=request.user.profile)

    for position in positions:

        # If there are applicants in a position add the position to applicants
        if position.any_applicants:
            for applicant in position.applicants.all():
                if applicant.rejected:
                    found_positions.add(applicant)
                    projects.append(position.related_project)
                    needed_skills.add(position.skill)

    return render(
        request,
        'profiles/rejected_applicants.html',
        {
            'applications_tab': 'Rejected',
            'found_positions': found_positions,
            'current_tab': 'Applications',  # navigation bar selector
            'needed_skills': list(needed_skills),
            'projects': projects
        })


"""Profile related views"""


@login_required
def profile_edit(request):
    """Allows a profile to be edited"""
    instance = request.user.profile
    form = forms.ProfileForm(instance=instance)

    # The form is currently not capturing images properly.
    if request.method == 'POST':
        form = forms.ProfileForm(
            request.POST, request.FILES, instance=instance
        )

        if form.is_valid():
            form.save()
            return redirect('profiles:profile', pk=request.user.profile.pk)

    return render(
        request,
        'profiles/edit.html',
        {
            'form': form,
            'current_tab': 'Profile'  # navigation bar selector
        })


def profile_view(request, pk):
    """Lets any user view a person's profile"""
    # Get the User model that matches the pk
    user_profile = get_object_or_404(models.Profile, pk=pk)
    projects = models.Project.objects.all().filter(owner=pk)\
        .prefetch_related('positions__skill')

    # Checks to see if the User has an avatar if not use default media
    try:
        image_url = static(user_profile.avatar.url)
    except ValueError:
        image_url = static('profiles_media/default_profile_image.png')

    return render(
        request,
        'profiles/profile.html',
        {
            'current_tab': 'Profile',  # navigation bar selector
            'image_url': image_url,
            'projects': projects,
            'user_profile': user_profile})


"""Project related views"""


@login_required()
def project_delete(request, pk):
    """Allows a project owner to delete a project"""
    project = get_object_or_404(models.Project, pk=pk)

    # Checks if the logged in user owns the project. If not kick them out.
    if project.owner.pk != request.user.profile.pk:
        raise Http404("You do not own this project.")

    project.delete()
    return redirect('profiles:homepage')


@login_required()
def project_delete_confirmation(request, pk):
    """Checks if a user really want to delete a project"""
    project = get_object_or_404(models.Project, pk=pk)

    # Checks if the logged in user owns the project. If not kick them out.
    if project.owner.pk != request.user.profile.pk:
        raise Http404("You do not own this project.")

    if request.method == 'POST':
        # If the user deleted the project return to homepage
        if request.POST.get('delete'):
            return redirect('profiles:project_delete', pk=pk)

        # If the user went back, go to the edit screen
        if request.POST.get('back'):
            return redirect('profiles:project_edit', pk=pk)

    return render (
        request,
        'profiles/project_delete_confirmation.html',
        {'project': project})


@login_required()
def project_edit(request, pk):
    """Allows only the project's owner to edit a project"""
    project = get_object_or_404(models.Project, pk=pk)

    # Checks if the logged in user owns the project. If not kick them out.
    if project.owner.pk != request.user.profile.pk:
        raise Http404("You do not own this project.")

    project_form = forms.ProjectForm(instance=project)
    # Currently only one position can be added per project. temporary
    position_form = forms.PositionForm(instance=project.positions.all()[0])

    if request.method == 'POST':
        project_form = forms.ProjectForm(request.POST, instance=project)

        # temporary, only get first position
        position_form = forms.PositionForm(
            request.POST, instance=project.positions.all()[0]
        )

        if project_form.is_valid() and position_form.is_valid():
            project_form.save()
            position_form.save()
            return redirect('profiles:project', pk=pk)

    return render(
        request,
        'profiles/project_edit.html',
        {
            'position_form': position_form,
            'project_form': project_form,
            'project': project
        })


@login_required()
def project_new(request):
    """Allows for the creation of a new project"""
    project_form = forms.ProjectForm()
    position_form = forms.PositionForm()

    if request.method == 'POST':
        project_form = forms.ProjectForm(request.POST)
        position_form = forms.PositionForm(request.POST)

        if project_form.is_valid() and position_form.is_valid():
            project_form.save()
            project = project_form.instance

            # Position needs to know which Project it belongs to
            position = position_form.save(commit=False)
            position.related_project = project
            position.save()

            # Get the saved position and add it to the project
            project.positions.add(position)
            return redirect('profiles:project', pk=project.pk)

    return render(
        request,
        'profiles/project_edit.html',
        {'project_form': project_form, 'position_form': position_form})


def project_view(request, pk):
    """Checks to see if the logged in user owns this project.
    If so show special owner template. If not show normal project template"""
    # Get the Project that matches the pk
    project = get_object_or_404(models.Project, pk=pk)

    # Makes sure there is a logged in user
    try:
        request.user.profile
    except AttributeError:
        pass
    else:
        if request.user.profile == project.owner:
            return render(
                request,
                'profiles/project_view_owned.html',
                {'project': project}
            )
    # If no logged in user or the wrong user the following happens
    return render(request, 'profiles/project.html', {'project': project})


@login_required
def project_view_all(request):
    """Shows the user all of their Projects regardless of filled status"""
    projects = models.Project.objects.all().filter(owner=request.user.profile)\
        .prefetch_related('positions__skill')

    # Get all of the desired skills for the projects
    needed_skills = set()

    positions = [project.positions.all() for project in projects]

    for position in positions:
        # Because positions is a list of queries we need to get
        # the first item with [0]
        needed_skills.add(position[0].skill)

    return render(
        request,
        'profiles/project_view_all.html',
        {
            'current_tab': 'My Projects',  # navigation bar selector
            'needed_skills': list(needed_skills),
            'projects': projects,
        }
    )


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
        Q(positions__skill__skill__contains=skill)).distinct()

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
