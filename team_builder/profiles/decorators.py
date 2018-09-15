from django.http import Http404


def logged_in_admin_or_staff_required(func):
    """Verifies that a user is logged in and staff or superuser."""
    def check_login(request, *args, **kwargs):
        if not (
                request.user.is_authenticated &
                (request.user.is_staff or request.user.is_superuser)
        ):
            raise Http404("You are not an admin or staff user!")
        return func(request, *args, **kwargs)
    return check_login
