# Social Team Builder
This is a website to help people find projects or create projects that
require a specific set of skills. Users can sign up to find projects or
post their own projects for others to join. Each user has their own custom
profile showcasing interests and talent. Upon attempting to join a project
the owner can accept or deny the application.

This website was built in part with HTML, CSS, and JavaScript originally
supplied from www.Teamtreehouse.com for a Python Web Development Tech Degree
Project. The HTML, CSS and JavaScript is to be considered built by Teamtreehouse for this project, but may be edited by me at some point.


## Starting

Create a virtualenv and install the project requirements, which are listed in
`requirements.txt`. The easiest way to do this is with `pip install -r
requirements.txt` while your virtualenv is activated.

Once this is done use the command `python manage.py migrate` to
initialize the database. Then run `python manage.py runserver` to
start the website on your local host.



## Todo List

This is the todo list for the Social Team Builder project. Any check mark
prefaced with a bullet point is an extra feature that can be added

- [x] Create site wide static files and templates

- [x] Add a custom User model that includes an avatar, bio, and username

- [x] Allow users to register for an account
* - [ ] Sign up email validation and complete the user's profile shortly
after sign up


- [x] Allow users to login with valid credentials

- [x] Let user's logout

- [x] Allow users to edit profile
* - [ ]Users can use Markdown in the "about me" part of the profile


- [x] Users can upload an avatar
* - [ ]The avatar image can be edited with tools like resize, crop, rotate and flip


- [ ] Users can pick multiple skills for their profile from a list
* - [ ]They can also create custom skills


- [x] Create a project
* - [ ]Markdown can be used in the project description


- [ ] Users can create multiple positions for a project
* - [ ]Can provide a time commitment for the position and use Markdown


- [ ] Can see applications for a project position
* - [ ]Allows user's to filter applicants


- [ ] Users can approve an applicant
* - [ ]They can approve applicants directly from the list page


- [ ] Users can reject an applicant
* - [ ]They can reject applicants directly from the list page


- [ ] I get notified if I am approved or denied a position

- [x] Can search by terms that match a project name or description. Search is also case-insensitive

- [x] Can filter open projects by skills needed
* - [ ]Their is a "projects for you" list with projects filtered by your skill set


- [ ] Can apply for a position
* - [ ]Can't apply for the same position twice, and filled positions are
displayed differently