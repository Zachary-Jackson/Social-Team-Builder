# Generated by Django 2.0.4 on 2018-06-20 23:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('any_applicants', models.BooleanField(default=False)),
                ('filled', models.BooleanField(default=False)),
                ('information', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='')),
                ('bio', models.CharField(blank=True, max_length=250)),
                ('username', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000)),
                ('requirements', models.CharField(max_length=150)),
                ('time_line', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=60)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Profile')),
                ('positions', models.ManyToManyField(blank=True, to='profiles.Position')),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='skills',
            field=models.ManyToManyField(blank=True, to='profiles.Skill'),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='position',
            name='applicants',
            field=models.ManyToManyField(blank=True, null=True, related_name='position_applicants', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='position',
            name='filled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_name', to='profiles.Profile'),
        ),
        migrations.AddField(
            model_name='position',
            name='position_creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.Profile'),
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
    ]
