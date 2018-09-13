from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import (AllSkills, Skill, Project, Position)


class BaseTest(TestCase):
    """This is the base setup class for the profile app tests"""

    def setUp(self):
        """Creates a Profile and some skills for testing"""

        # Creates a couple of Skill(s)
        self.skill_1 = Skill.objects.create(skill='Django developer')
        self.skill_2 = Skill.objects.create(skill='Angular')
        self.skill_3 = Skill.objects.create(skill='Mountain Climbing')

        # Get the current User model
        user = get_user_model()

        # Create the first user for testing
        self.user = user.objects.create_superuser(
            email='user@user.com',
            username='Santa',
            password='testpass'
        )
        self.user.bio = (
            'The weather forecast shows snow for the next five months.'
        )
        self.user.save()
        self.user_1_skills = AllSkills.objects.create(user_id=self.user.pk)
        self.user_1_skills.skills.add(self.skill_1, self.skill_2)

        # Creates a second user
        user = get_user_model()
        self.user_2 = user.objects.create_superuser(
            email='user2@user2.com',
            username='Hattie',
            password='testpass',
        )
        self.user_2.bio = 'I am a wild little dog.'
        self.user_2.save()
        self.user_2_skills = AllSkills.objects.create(user_id=self.user_2.pk)
        self.user_2_skills.skills.add(self.skill_1, self.skill_3)


class BaseTestWithPositionsProjects(BaseTest):
    """Inherits from BaseTest and adds positions and projects to setUp"""

    def setUp(self):
        """Adds various positions and projects to setUp()"""
        super().setUp()

        # Creates a Project
        self.project = Project.objects.create(
            owner=self.user, title='Test Project',
            time_line='Depends on the number of features',
            requirements='See the README.md', description='also see README.md'
        )

        # Creates a Position to attach to a Project
        self.position = Position.objects.create(
            skill=self.skill_1, information='this is the position',
            related_project=self.project
        )

        # add a position to the main project
        self.project.positions.add(self.position)