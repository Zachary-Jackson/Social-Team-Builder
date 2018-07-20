from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    # Miscellaneous related paths
    path('', views.HomepageListView.as_view(), name='homepage'),
    path('login_router', views.login_router, name='login_router'),

    # Applications related paths
    path('applications', views.applications, name='applications'),

    path('applications/accept/<int:position_pk>/<int:profile_pk>',
         views.applications_accept,
         name='applications_accept'),

    path('applications/reject/<int:position_pk>/<int:profile_pk>',
         views.applications_reject,
         name='applications_reject'),

    path('applications/request/<int:pk>',
         views.applications_request,
         name='applications_request'),

    path('applications/view/accepted',
         views.applications_view_accepted,
         name='applications_view_accepted'),

    path('applications/view/rejected',
         views.applications_view_rejected,
         name='applications_view_rejected'),

    # Profile related paths
    path('profile/edit/', views.profile_edit, name='edit'),
    path('profile/view/<int:pk>/', views.profile_view, name='profile'),

    # Project related paths
    path(
        'project/delete/<int:pk>',
        views.project_delete,
        name='project_delete'
    ),
    path(
        'project/delete_confirmation/<int:pk>',
        views.project_delete_confirmation,
        name='project_delete_confirmation'
    ),
    path('project/edit/<int:pk>', views.project_edit, name='project_edit'),
    path('project/new', views.project_new, name='project_new'),
    path('project/view/<int:pk>/', views.project_view, name='project'),

    # Search related paths
    path('search', views.search, name='search'),
    path(
        'search/skill/<str:skill>',
        views.search_by_skill,
        name='search_by_skill'
    ),
    path('search/your_skills',
         views.search_your_skills,
         name='search_your_skills'
    ),
    path('project/view_all', views.project_view_all, name='project_view_all'),
]
