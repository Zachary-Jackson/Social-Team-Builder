from django.shortcuts import render


def homepage(request):
    """This is the hompage for the social team builder project"""
    # Please note this view is likely temporary
    return render(request, 'team_builder/homepage.html')
