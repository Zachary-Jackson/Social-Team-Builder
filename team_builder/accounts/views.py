from django.urls import reverse_lazy
from django.views import generic

from . import forms


class SignUp(generic.CreateView):
    """Allows the user to sign up for an account"""
    form_class = forms.UserCreateForm
    success_url = reverse_lazy("homepage")
    template_name = "accounts/sign_up.html"
