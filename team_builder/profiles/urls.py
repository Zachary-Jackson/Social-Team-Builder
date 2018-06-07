from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('profile/edit/', views.profile_edit, name='edit'),
    path('profile/view/<int:pk>/', views.profile_view, name='profile'),
    path('project/delete/<int:pk>', views.project_delete, name='project_delete'),
    path('project/edit/<int:pk>', views.project_edit, name='project_edit'),
    path('project/new', views.project_new, name='project_new'),
    path('project/view/<int:pk>/', views.project_view, name='project'),
    path('login_router', views.login_router, name='login_router')
]
