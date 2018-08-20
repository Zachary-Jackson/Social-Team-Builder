# Social Team Builder
This is a website to help people find projects or create projects that
require a specific set of skills. Users can sign up to find projects or
post their own projects for others to join. Each user has their own custom
profile showcasing interests and talent. Upon attempting to join a project
the owner can accept or deny the application.

This website was built in part with HTML, CSS, and JavaScript originally
supplied from www.Teamtreehouse.com for a Python Web Development Tech Degree
Project. The HTML, CSS and JavaScript is to be considered built by 
Teamtreehouse for this project, but may be edited by me at some point.


## Starting

Create a virtualenv and install the project requirements, which are listed in
`requirements.txt`. The easiest way to do this is with `pip install -r
requirements.txt` while your virtualenv is activated.

In order to run this project you need to create a SECRET_KEY. In the
team_builder directory create a file called `secret_key.py` that has a
secret_key variable.
Once this is done use the command `python manage.py migrate` to
initialize the database. Then run `python manage.py runserver` to
start the website on your local host.

## Requirements

In addition to the requirements.txt file, python 3.5 + is required
due to type hinting.