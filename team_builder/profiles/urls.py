from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('edit/', views.profile_edit, name='edit'),
    path('view/<int:pk>/', views.profile_view, name='profile'),
    path('login_router', views.login_router, name='login_router')
]
