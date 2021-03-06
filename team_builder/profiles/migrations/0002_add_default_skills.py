# Generated by Django 2.0.4 on 2018-06-07 18:48

from django.db import migrations


def add_default_skills(apps, schema_editor):
    """Adds a couple of skill objects to the database"""
    skills = apps.get_model('profiles', 'Skill')

    positions = ['Android Developer', 'Designer', 'Java Developer',
                 'JavaScript Developer','PHP Developer', 'Python Developer',
                 'Rails Developer','WordPress Developer', 'iOS Developer']
    for position in positions:
        skills.objects.create(skill=position)


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default_skills)
    ]
