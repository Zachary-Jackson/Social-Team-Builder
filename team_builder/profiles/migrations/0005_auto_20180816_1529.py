# Generated by Django 2.0.4 on 2018-08-16 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_skillconfirmation_pending'),
    ]

    operations = [
        migrations.AddField(
            model_name='skillconfirmation',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='skillconfirmation',
            name='pending',
            field=models.BooleanField(default=True),
        ),
    ]
