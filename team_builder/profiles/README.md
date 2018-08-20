# profiles

## General info

This is an application designed to help people find projects or create
projects that require a specific set of skills. Users can find projects, or
post their own projects for others to join. Each user has their own custom
profile showcasing interests and talents. Upon attempting to join a project
the owner can accept or deny the application.

Various resources can be found in the resources directory. JavaScript files
need to be added to the static 'js' folder, 
while the image needs to be placed in the profiles_media directory in the
static files path. (only for new projects)

### Requirements

1) django-notifications-hq==1.5.0 (to send notifications)

2) A custom User model with an avatar and a bio field that is markdown
compliant with the property bio_markdown that displays the bio in markdown.

3) django-markdownx==2.0.23 (for various fields in models.py)

4) Inside of assets there needs to be a directory called *profiles_media*
that contains an image called *default_profile_image.png*. This image
will be used if the user does not have a profile image.

5) Internet connection for a jQuery request