from django.contrib import admin

from . import models

admin.site.register(models.AuthenticationToken)


class UserAdmin(admin.ModelAdmin):
    """The admin page for the custom user model"""
    fields = (
        'username', 'email', 'avatar', 'bio', 'color', 'is_active',
        'is_staff', 'date_joined',
    )


admin.site.register(models.User, UserAdmin)