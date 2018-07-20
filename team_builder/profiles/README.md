# profiles

## General info

This is an application designed to help people find projects or create
projects that require a specific set of skills. Users can find projects, or
post their own projects for others to join. Each user has their own custom
profile showcasing interests and talents. Upon attempting to join a project
the owner can accept or deny the application.

### Requirements

1) django-notifications-hq==1.5.0 (to send notifications)

2) A custom User model with an avatar and a bio field that is markdown
compliant with the property bio_markdown that displays the bio in markdown.

3) django-markdownx==2.0.23 (for various fields in models.py)