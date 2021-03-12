from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import User, Course, Lesson
from markdown2 import markdown
from dotenv import load_dotenv
import json
import requests
import os
load_dotenv()

clientSecret = os.getenv('clientSecret')
clientId = os.getenv('clientId')


def landing(request):
    return render(request, "landing.html")


@login_required(login_url='login')
def courses(request):
    course_list = Course.objects.all()

    progress = []
    for course in course_list:
        total = len(course.lesson_set.all())
        completed = len(request.user.completed_lessons.filter(course=course))
        progress.append([completed, total, completed/total*100])
    # print(list(zip(course_list, progress)))

    return render(request, "courses.html", {
        'course_list': zip(course_list, progress)
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
    try:
        curr_lesson = Lesson.objects.filter(
            course=course).exclude(users_completed=request.user)[0]
    except:
        curr_lesson = 'last_lesson'
    return render(request, 'course_view.html', {
        'course': course,
        'curr_lesson': curr_lesson
    })


def lesson_view(request, lesson_id):
    lesson = Lesson.objects.get(pk=lesson_id)
    try:
        lesson_description = markdown(lesson.lesson_description)
    except:
        lesson_description = ''
    try:
        curr_lesson = Lesson.objects.filter(
            course=lesson.course).exclude(users_completed=request.user)[0]
    except:
        curr_lesson = lesson

    return render(request, 'lesson_view.html', {
        'lesson': lesson,
        'lesson_description': lesson_description,
        'next_lesson': Lesson.objects.filter(course=lesson.course, id__gt=lesson.id).first(),
        'prev_lesson': Lesson.objects.filter(course=lesson.course, id__lt=lesson.id).last(),
        'curr_lesson': curr_lesson
    })


def codeengine(script, lang="python3", stdin=""):
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
    }

    script = json.dumps(script)
    stdin = json.dumps(stdin)

    data = '''{"clientId": "''' + clientId + '''",
            "clientSecret":"''' + clientSecret + '''",
            "script":''' + script + ''',
            "language":"''' + lang + '''",
            "stdin":''' + stdin + ''',
            "versionIndex":"0"}'''

    response = requests.post(
        'https://api.jdoodle.com/v1/execute', headers=headers, data=data)

    return response


@csrf_exempt
def runcode(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse("landing"))

    data = json.load(request)
    response = codeengine(data['script'], data['lang'], data['stdin'])
    return JsonResponse(response.json())


@csrf_exempt
def submitcode(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse("landing"))

    data = json.load(request)
    lesson = Lesson.objects.get(pk=data['lessonid'])

    for testcase in lesson.testcase_set.all():
        response = codeengine(data['script'], data['lang'], testcase.input)
        output = response.json()['output']
        # print(output.strip(), testcase.output.strip())
        if (output.strip() != testcase.output.strip()):
            return JsonResponse({"verdict": "fail"})

    request.user.completed_lessons.add(lesson)

    return JsonResponse({"verdict": "pass"})


@csrf_exempt
def claimcert(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse("landing"))

    data = json.load(request)
    course = Course.objects.get(pk=data["courseid"])
    print(course)

    return JsonResponse({"verdict": "pass"})
