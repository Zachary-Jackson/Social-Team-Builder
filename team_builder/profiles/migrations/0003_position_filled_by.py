# Generated by Django 2.0.4 on 2018-06-14 00:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_add_default_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='filled_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='profiles.Profile'),
        ),
    ]
