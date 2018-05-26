from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views import generic

from . import forms


class LoginView(generic.FormView):
    """This class logs in a user and redirects them to the homepage"""
    form_class = AuthenticationForm
    success_url = reverse_lazy("profiles:login_router")
    template_name = "accounts/sign_in.html"

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request, **self.get_form_kwargs())

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class LogoutView(generic.RedirectView):
    url = reverse_lazy("homepage")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class SignUp(generic.CreateView):
    """Allows the user to sign up for an account"""
    form_class = forms.UserCreateForm
    success_url = reverse_lazy("accounts:login")
    template_name = "accounts/sign_up.html"
