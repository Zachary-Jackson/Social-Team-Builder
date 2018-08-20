from django.conf import settings
from django.db import models

# django-markdownx
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class AllSkills(models.Model):
    """Holds on to all of the skills for a user"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE
    )
    skills = models.ManyToManyField('Skill', blank=True)

    def __str__(self):
        """Shows the user's username + skills"""
        username = self.user.username
        return f"{username}'s skills"


class Skill(models.Model):
    """A class that represents a single skill"""
    skill = models.CharField(max_length=35, unique=True)

    def __str__(self):
        return self.skill

    def readable_to_url(self):
        """Takes the name of the skill and changes spaces to underlines"""
        return self.skill.replace(' ', '_')


class SkillConfirmation(models.Model):
    """
    A class that holds onto a potential Skill object and
    the the User who suggested it for verification
    """
    accepted = models.BooleanField(default=False)

    # The user who created the potential skill
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    pending = models.BooleanField(default=True)

    # Skill is not unique in case a skill is denied, then accepted
    skill = models.CharField(max_length=35)

    def __str__(self):
        if self.pending:
            return 'Pending skill: {}'.format(self.skill)
        else:
            return 'Non-pending skill: {}'.format(self.skill)


class Project(models.Model):
    """This is the model for a Project"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    description = MarkdownxField(max_length=1000)
    positions = models.ManyToManyField('Position', blank=True)
    requirements = models.CharField(max_length=100)
    time_line = models.CharField(max_length=30)
    title = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.title

    @property
    def description_markdown(self):
        """This allows us to turn self.description into markdown to send
        to a template for display."""
        return markdownify(self.description)


class Position(models.Model):
    """This holds onto position information for a Project"""
    related_project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        blank=True)

    # applicants hold every User that has applied to this position
    applicants = models.ManyToManyField(
        'Applicants',
        related_name='position_applicants',
        blank=True,
    )

    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)

    # filled and filled_by are for final application acceptance
    # current applicants are found in the Applicants model
    filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='employee_name'
    )

    information = models.CharField(max_length=500)
    time_commitment = MarkdownxField(max_length=400)

    def __str__(self):
        """Returns the skill and information with ... if info is to long"""
        information = self.information
        if len(information) > 30:
            return "{}: {}...".format(str(self.skill), self.information[:30])
        return "{}: {}".format(str(self.skill), self.information)

    def save(self, *args, **kwargs):
        """automatically sets the filled_by position"""

        # this try except block sets the self.filled position
        try:
            self.filled_by.pk
        except:
            self.filled = False
        else:
            self.filled = True

        super(Position, self).save(*args, **kwargs)

    @property
    def time_commitment_markdown(self):
        """This allows us to turn self.time_commitment into markdown to send
        to a template for display."""
        return markdownify(self.time_commitment)


class Applicants(models.Model):
    """Contains an applicant and what project they belong to"""
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        related_name='applicants_position'
    )

    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        """Shows the User's name and Applicant pk"""
        return str(self.applicant)