from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Allows for the creation of Users and SuperUsers"""

    def create_user(self, email, password):
        """Creates and saves a User with the given email and password"""
        if not email:
            raise ValueError("An email adress must be provided")
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        """Creates and saves a SuperUser"""
        user = self.create_user(
            email,
            password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """This is a new default User class"""
    date_joined = models.DateTimeField(default=timezone.now)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # The email field is used as the "username" to log-in
    # because only one user presumably knows it
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
