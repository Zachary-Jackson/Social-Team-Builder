# Generated by Django 2.0.4 on 2018-06-21 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_add_default_skills'),
    ]

    operations = [
        migrations.CreateModel(
            name='Applicants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('new_applicant', models.BooleanField(default=True)),
                ('rejected', models.BooleanField(default=False)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.Profile')),
            ],
        ),
        migrations.AlterField(
            model_name='position',
            name='applicants',
            field=models.ManyToManyField(blank=True, related_name='position_applicants', to='profiles.Applicants'),
        ),
    ]
