from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path(
        'email_confirmation/',
        views.email_confirmation_view,
        name='email_confirmation'
    ),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.sign_up, name='signup'),
    path(
        'token_confirmation/<str:token>/',
        views.token_confirmation_view,
        name='token_confirmation'
    ),
]
