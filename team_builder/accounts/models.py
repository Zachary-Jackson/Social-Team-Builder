import datetime
from io import BytesIO

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone

from PIL import Image

# django-markdownx
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class UserManager(BaseUserManager):
    """Allows for the creation of Users and SuperUsers"""

    def create_user(self, email, username, password):
        """Creates and saves a User with the given email, username
         and password"""
        if not email:
            raise ValueError("An email address must be provided")
        user = self.model(
            email=self.normalize_email(email),
            username=username
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password):
        """Creates and saves a SuperUser"""
        user = self.create_user(
            email,
            username,
            password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """This is a new default User class"""
    # The following are set/created by the accounts application
    date_joined = models.DateTimeField(default=timezone.now)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    username = models.CharField(max_length=50, unique=True)

    # These are not set by accounts
    avatar = models.ImageField(null=True, blank=True)
    bio = MarkdownxField(max_length=500, blank=True)
    color = models.CharField(max_length=50, blank=True)

    objects = UserManager()

    # The email field is used as the "username" to log-in
    # because only one user presumably knows it
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    @property
    def bio_markdown(self):
        """This allows us to turn self.bio into markdown to send
        to a template for display."""
        return markdownify(self.bio)

    def save(self, *args, **kwargs):
        """
        Double checks the size of the avatar. If the image is to big
        shrink it down below 500x500
        """

        # This function was writen with help in part from this stack overflow
        # post  (https://stackoverflow.com/questions/22035833/
        # how-to-go-form-django-image-field-to-pil-image-and-back)
        super(User, self).save(*args, **kwargs)

        # Checks if the image is larger than 500 x 500
        avatar = self.avatar

        # If the user does not have an avatar pass
        try:
            height = avatar.height
            width = avatar.width

        except ValueError:
            pass

        else:
            # If the height or width is lower than 500 we are good
            if height > 500 or width > 500:
                # Open the image in Pillow
                image = Image.open(avatar.open())

                size = (500, 500)
                image.thumbnail(size)

                file = BytesIO()

                image.save(file, format='png')
                # This will call this save() method recursively once
                self.avatar.save(
                    self.avatar.name, ContentFile(file.getvalue())
                )


class AuthenticationToken(models.Model):
    """
    Holds onto a token for user verification

    Can be used to verify token.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        unique=True,
        on_delete=models.CASCADE)

    token = models.CharField(max_length=1000)

    expiration_date = models.DateTimeField()

    def __str__(self):
        """Creates a string value for AuthenticationToken"""
        return "{}: token".format(self.user)

    def is_valid(self, token):
        """Checks if a token is valid and has not expired"""
        # Does the token match the set token
        if not self.token == token:
            return False

        # Has the token expired?
        current_time = datetime.datetime.now(datetime.timezone.utc)
        if current_time > self.expiration_date:
            return False

        # Otherwise
        return True
