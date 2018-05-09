from django.conf import settings
from django.db import models


class Profile(models.Model):
    """This is the profile model for a user"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True)
    bio = models.CharField(max_length=250, blank=True)
    skills = models.ManyToManyField('Skill', blank=True)

    def __str__(self):
        return "{}'s profile".format(self.user.username)


class Skill(models.Model):
    """A class that represents a single skill"""
    skill = models.CharField(max_length=100)

    def __str__(self):
        return self.skill
