## notification_hub

## General info

This application is designed to display notifications that were created
using the *django-notifications-hq* package. Any notification can be shown
marked as read, unread, or deleted. No notifications are created here.

This app would probably be called notifications, but that interferes with 
the *django-notifications-hq* package.Thus the notification_hub name.

### Requirements

django-notifications-hq==1.5.0

The templates have five sections that are used.

* A "title_tag"

* "header" which is where the main title goes

* "first_sidebar" which is where the main notification selector goes

* "body_header" where the body's title goes

* "body" where the main content goes that displays the list of notifications

 The current_tab template variable can be left in or removed.