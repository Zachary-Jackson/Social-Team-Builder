import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic

from . import forms
from . import models


def create_email_verification_token(user: models.User) -> None:
    """
    Create an email_verification token that can be used to authenticate
    a user.
    """
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)

    # Create an AuthenticationToken object for the user
    expiration_date = datetime.datetime.now() + datetime.timedelta(days=1)

    models.AuthenticationToken.objects.create(
        user=user,
        token=token,
        expiration_date=expiration_date
    )


def get_url(request, user: models.User) -> str:
    """Takes a user and return a url for an authentication token"""
    site_url = request.get_host()
    token = user.authenticationtoken.token

    url = site_url + '/accounts/token_confirmation/' + token + '/'

    return url


def send_confirmation_email(user, url: str) -> None:
    """
    Takes a user object and sends the user a validation email
    """

    # If user is already active, 404
    if user.is_active:
        raise(Http404('This action is not authorized'))

    # Get all of the information for an email
    header = 'Team Builder: Email Verification required!'
    body = (
        'In order to activate your account at Team Builder please '
        'click the link bellow.\n'
        f'{url}'
    )
    recipient_email = [user.email]

    email = EmailMessage(header, body, to=recipient_email)
    email.send()


"""Accounts views"""


def email_confirmation_view(request):
    """Shows the user the email_confirmation view"""
    return render(request, 'accounts/email_confirmation.html')


class LogoutView(LoginRequiredMixin, generic.RedirectView):
    """Allows a user to logout"""
    url = reverse_lazy("profiles:homepage")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


def sign_up(request):
    """Allows a user to sign up for an account"""
    if request.POST:
        user_form = forms.UserCreateForm(
            request.POST
        )
        user = user_form.save()

        # Creates a token to authenticate the user
        create_email_verification_token(user)

        # Send the user an email verification
        url = get_url(request, user)
        send_confirmation_email(user, url)

        return redirect('accounts:email_confirmation')

    user_form = forms.UserCreateForm()
    return render(
        request,
        'accounts/sign_up.html',
        {'form': user_form}
    )


def token_confirmation_view(request, token: str):
    """Ensures a token is valid, if so activate user"""
    # Tries to find the user or 404
    try:
        found_user = models.AuthenticationToken.objects.get(token=token)
    except:
        raise Http404("Invalid Token")

    # Check if the token is expired
    valid = found_user.is_valid(token)

    if valid:
        user_model = found_user.user
        user_model.is_active = True
        user_model.save()

        # Login the user
        login(request, user_model)
        return redirect('profiles:login_router')
    else:
        raise Http404("Invalid Token")