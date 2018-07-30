# accounts

## General info

This application is a custom user model for a Django project. The user model
has an email address field which is classified as the username for tasks such
as logging in. The username field is required and is shown instead of an email
address protecting the user's email account.

Accounts allows users to logout and signup on the web page. For tasks such as
logging in, and password reset along with email confirmation, that is all
handled by `*'django.contrib.auth.urls'*`

### Fields

1) date_joined: is the date the User model was created

2) email: is the username field for this User model

3) is_active/is_staff: are used for admin type things and are created
like the standard Django user model

4) username: required and is displayed instead of the email in strings

### Miscellaneous fields

These are various fields that are not required or used for the accounts app
, and are primarily here for other apps.

1) avatar: this is a standard ImageField

2) bio: The bio field is markdown capable, and is a MarkdownxField. This 
requires the django-markdownx package. A custom property bio_markdown has been
added to the User class for easy markdown display to the browser.

### Requirements

django-markdownx==2.0.23
