from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import generic

from . import forms


class LogoutView(LoginRequiredMixin, generic.RedirectView):
    """Allows a user to logout"""
    url = reverse_lazy("profiles:homepage")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class SignUpView(generic.CreateView):
    """Allows the user to sign up for an account"""
    form_class = forms.UserCreateForm
    success_url = reverse_lazy("login")
    template_name = "accounts/sign_up.html"
