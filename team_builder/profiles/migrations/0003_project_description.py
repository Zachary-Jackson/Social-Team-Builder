# Generated by Django 2.0.4 on 2018-05-31 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_position_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.CharField(default='Description', max_length=1000),
            preserve_default=False,
        ),
    ]
