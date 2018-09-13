from django.urls import reverse


from .base_tests import BaseTest
from ..models import (Skill, SkillConfirmation)


class AdminTests(BaseTest):
    """Tests all the views from administrative views"""

    def test_administrative(self):
        """Tests the main administrative page"""
        self.client.login(username='user@user.com', password='testpass')

        # Create a SkillsConfirmation object
        skill = SkillConfirmation.objects.create(
            creator=self.user_2, skill='New Skill'
        )

        resp = self.client.get(reverse('profiles:administrative'))

        # page information
        self.assertContains(resp, 'Administrative')
        self.assertContains(resp, 'Pending Tasks')
        self.assertContains(resp, 'Non-pending Tasks')

        # Skill information
        self.assertContains(resp, str(skill))
        self.assertContains(resp, 'Accept Skill')
        self.assertContains(resp, 'Deny Skill')

    def test_administrative_non_pending(self):
        """Tests the main administrative completed tasks page"""
        self.client.login(username='user@user.com', password='testpass')

        # Create a SkillsConfirmation object
        skill = SkillConfirmation.objects.create(
            creator=self.user_2, skill='New Skill',
            accepted=True, pending=False
        )

        resp = self.client.get(reverse('profiles:administrative_non_pending'))

        # page information
        self.assertContains(resp, 'Administrative')
        self.assertContains(resp, 'Pending Tasks')
        self.assertContains(resp, 'Non-pending Tasks')

        # Skill information
        self.assertContains(resp, str(skill))
        self.assertContains(resp, 'Accepted')

    def test_skill_accept(self):
        """Ensures skills can be accepted"""
        self.client.login(username='user@user.com', password='testpass')

        # Create a SkillsConfirmation object
        skill_confirmation = SkillConfirmation.objects.create(
            creator=self.user_2, skill='New Skill'
        )

        resp = self.client.get(
            reverse(
                'profiles:skill_accept',
                kwargs={'pk': skill_confirmation.pk}
                )
        )

        # Refresh the skill variable
        skill_confirmation = SkillConfirmation.objects.get(
            pk=skill_confirmation.pk
        )

        # Ensure that the SkillConfirmation was updated
        self.assertTrue(skill_confirmation.accepted)
        self.assertFalse(skill_confirmation.pending)

        # Ensure we have a new skill
        self.assertTrue(Skill.objects.get(skill=skill_confirmation.skill))

        # Check if self.user_2 has the new skill
        found_skill = self.user_2.allskills.skills.filter(
            skill=skill_confirmation.skill
        )

        self.assertTrue(found_skill)

    def test_skill_deny(self):
        """Ensures skills can be denied"""
        self.client.login(username='user@user.com', password='testpass')

        # Create a SkillsConfirmation object
        skill_confirmation = SkillConfirmation.objects.create(
            creator=self.user_2, skill='New Skill'
        )

        resp = self.client.get(
            reverse(
                'profiles:skill_deny',
                kwargs={'pk': skill_confirmation.pk}
                )
        )

        # Refresh the skill variable
        skill_confirmation = SkillConfirmation.objects.get(
            pk=skill_confirmation.pk
        )

        # Ensure that the SkillConfirmation was updated
        self.assertFalse(skill_confirmation.accepted)
        self.assertFalse(skill_confirmation.pending)

        # Ensure we do not have a new skill
        self.assertFalse(Skill.objects.filter(skill=skill_confirmation.skill))

        # Check if self.user_2 does not have the new skill
        found_skill = self.user_2.allskills.skills.filter(
            skill=skill_confirmation.skill
        )

        self.assertFalse(found_skill)
