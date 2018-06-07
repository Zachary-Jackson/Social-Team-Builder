from django.conf import settings
from django.db import models


class Profile(models.Model):
    """This is the profile model for a user"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    username = models.CharField(max_length=100, unique=True)
    avatar = models.ImageField(null=True, blank=True)
    bio = models.CharField(max_length=250, blank=True)
    skills = models.ManyToManyField('Skill', blank=True)

    def __str__(self):
        return self.username


class Skill(models.Model):
    """A class that represents a single skill"""
    skill = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.skill


class Project(models.Model):
    """This is the model for a Project"""
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    positions = models.ManyToManyField('Position')
    time_line = models.CharField(max_length=50)
    requirements = models.CharField(max_length=150)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.title


class Position(models.Model):
    """This holds onto position information for a Project"""
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)
    information = models.CharField(max_length=500)
    # Eventually filled will need to know who filled a position
    filled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.skill)