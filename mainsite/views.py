from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import User, Course, Lesson


def landing(request):
    return render(request, "landing.html")


@login_required(login_url='login')
def courses(request):
    course_list = Course.objects.all()
    return render(request, "courses.html", {
        'course_list': course_list
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("courses"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('landing'))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("courses"))
    else:
        return render(request, "register.html")


@login_required(login_url='login')
def profile_edit(request):
    if request.method == 'POST':
        logged_user = User.objects.get(pk=request.user.pk)
        logged_user.first_name = request.POST['first_name']
        logged_user.last_name = request.POST['last_name']
        logged_user.user_summary = request.POST['summary']
        logged_user.linkedin_url = request.POST['linkedin_url']
        logged_user.twitter_url = request.POST['twitter_url']
        logged_user.github_url = request.POST['github_url']
        logged_user.save()
        return HttpResponseRedirect(reverse('edit_profile'))
    return render(request, 'profile_edit.html')


def profile_view(request, username):
    user = User.objects.get(username=username)
    return render(request, 'profile_view.html', {'user': user})


def course_view(request, course_id):
    course = Course.objects.get(pk=course_id)
    return render(request, 'course_view.html', {'course': course})
