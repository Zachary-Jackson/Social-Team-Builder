from django.conf import settings
from django.db import models


class Profile(models.Model):
    """This is the profile model for a user"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    avatar = models.ImageField(null=True, blank=True)
    bio = models.CharField(max_length=500, blank=True)
    skills = models.ManyToManyField('Skill', blank=True)
    username = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.username


class Skill(models.Model):
    """A class that represents a single skill"""
    skill = models.CharField(max_length=35, unique=True)

    def __str__(self):
        return self.skill

    def readable_to_url(self):
        """Takes the name of the skill and changes spaces to underlines"""
        return self.skill.replace(' ', '_')


class Project(models.Model):
    """This is the model for a Project"""
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    positions = models.ManyToManyField('Position', blank=True)
    requirements = models.CharField(max_length=100)
    time_line = models.CharField(max_length=30)
    title = models.CharField(max_length=40)

    def __str__(self):
        return self.title


class Position(models.Model):
    """This holds onto position information for a Project"""
    # allows various positions to easily be found by a Profile
    # position_creator will automatically be set from the
    # related_project
    position_creator = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    related_project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        blank=True)

    # applicants hold every Profile that has applied to this position
    applicants = models.ManyToManyField(
        'Applicants',
        related_name='position_applicants',
        blank=True,
    )

    # if there are any applicants, any_applicants will automatically
    # default to true
    any_applicants = models.BooleanField(default=False)

    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)
    # filled and filled_by are for final application acceptance
    # current applicants are found in the Applicants model
    filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='employee_name'
    )
    information = models.CharField(max_length=500)

    def __str__(self):
        """Returns the skill and information with ... if info is to long"""
        information = self.information
        if len(information) > 30:
            return "{}: {}...".format(str(self.skill), self.information[:30])
        return "{}: {}".format(str(self.skill), self.information)

    def save(self, *args, **kwargs):
        """automatically fills a position and the position_creator"""

        # this try except block sets the self.filled position
        try:
            self.filled_by.pk
        except:
            self.filled = False
        else:
            self.filled = True

        # sets the position_creator value automatically to reduce
        # potential errors

        self.position_creator = self.related_project.owner

        super(Position, self).save(*args, **kwargs)


class Applicants(models.Model):
    """Contains an applicant and what project they belong to"""
    applicant = models.ForeignKey(Profile, on_delete=models.CASCADE)
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='applicants_position'
    )

    accepted = models.BooleanField(default=False)
    new_applicant = models.BooleanField(default=True)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        """Shows the User's name and Applicant pk"""
        return str(self.applicant)