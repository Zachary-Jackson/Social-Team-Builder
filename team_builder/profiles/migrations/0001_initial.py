# Generated by Django 2.0.4 on 2018-07-29 04:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import markdownx.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AllSkills',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Applicants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('rejected', models.BooleanField(default=False)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('any_applicants', models.BooleanField(default=False)),
                ('filled', models.BooleanField(default=False)),
                ('information', models.CharField(max_length=500)),
                ('time_commitment', markdownx.models.MarkdownxField(max_length=400)),
                ('applicants', models.ManyToManyField(blank=True, related_name='position_applicants', to='profiles.Applicants')),
                ('filled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_name', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', markdownx.models.MarkdownxField(max_length=1000)),
                ('requirements', models.CharField(max_length=100)),
                ('time_line', models.CharField(max_length=30)),
                ('title', models.CharField(max_length=40, unique=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('positions', models.ManyToManyField(blank=True, to='profiles.Position')),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.CharField(max_length=35, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='position',
            name='related_project',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.Project'),
        ),
        migrations.AddField(
            model_name='position',
            name='skill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Skill'),
        ),
        migrations.AddField(
            model_name='applicants',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applicants_position', to='profiles.Position'),
        ),
        migrations.AddField(
            model_name='allskills',
            name='skills',
            field=models.ManyToManyField(blank=True, to='profiles.Skill'),
        ),
        migrations.AddField(
            model_name='allskills',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
