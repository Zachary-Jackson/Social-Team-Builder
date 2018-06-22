from django.contrib import admin

from . import models

admin.site.register(models.Applicants)
admin.site.register(models.Profile)
admin.site.register(models.Skill)
admin.site.register(models.Project)
admin.site.register(models.Position)