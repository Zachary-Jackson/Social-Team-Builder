# accounts

## General info

This application is a custom user model for a Django project. The user model
has an email address field which is classified as the username for tasks such
as logging in. The username field is required and is shown instead of an email
address protecting the user's email account.

By default a user is not active. In order to activate a user by default
use create_superuser, otherwise the user must follow the emailed instructions.
A package could have been used for this, but doing it manually is good
practice and lowers dependencies.

Accounts allows users to logout and signup on the web page. For tasks such as
logging in, and password reset along with email confirmation, that is all
handled by `*'django.contrib.auth.urls'*`

### Fields

User Fields

1) date_joined: is the date the User model was created

2) email: is the username field for this User model

3) is_active/is_staff: are used for admin type things and are created
like the standard Django user model

4) username: required and is displayed instead of the email in strings

AuthenticationToken Fields

1) user: The user associated with a token

2) token: The token string used to authenticate a user

3) expiration_date: When a token expires

### Miscellaneous fields

These are various fields that are not required or used for the accounts app
, and are primarily here for other apps.

1) avatar: this is a standard ImageField

2) bio: The bio field is markdown capable, and is a MarkdownxField. This 
requires the django-markdownx package. A custom property bio_markdown has been
added to the User class for easy markdown display to the browser.

### Requirements

django-markdownx==2.0.23

Email Backend