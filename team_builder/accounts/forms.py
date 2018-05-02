from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class UserCreateForm(UserCreationForm):
    """A form that gets the required fields for a custom user model"""
    class Meta:
        fields = ("email", "username", "password1", "password2")
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Email adress"
        self.fields["username"].label = "Display name"
