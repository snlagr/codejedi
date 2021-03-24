import json
import requests
import os
import email
import smtplib
import ssl
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
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import Image, ImageDraw, ImageFont
load_dotenv()

clientSecret = os.getenv('clientSecret')
clientId = os.getenv('clientId')
sender_email = os.getenv('sender_email')
password = os.getenv('password').replace('@', '#')
rapidAPIkey = os.getenv('rapidAPIkey')
rapidAPIkey1 = os.getenv('rapidAPIkey1')
rapidAPIkey2 = os.getenv('rapidAPIkey2')
count = 0

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
        sendEmail(email, "Welcome to CodeJedi",
                  "Hope you have a great journey with us.")
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
        logged_user.email = request.POST['email']
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
    course = Course.objects.get(pk=data["courseid"]).course_title
    name = request.user.first_name + " " + request.user.last_name
    cert_data = {
        "name": name,
        "course": course
    }
    sendEmail(request.user.email, 'Collect your certificate!',
              'Congratulations for completing the course.', cert_data)
    return JsonResponse({"verdict": "pass"})


def sendEmail(receiver_email, subject, body, cert_data=None):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = "CodeJedi " + sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    # message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    if cert_data:
        img = Image.open('certificate.jpg')
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype('arial.ttf', 100)
        name = cert_data["name"]
        x = img.width//2 - len(name) * 23
        draw.text(xy=(x, 650), text=name, fill=(0, 0, 0), font=font)

        font = ImageFont.truetype('arial.ttf', 50)
        course = "For completion of " + \
            cert_data["course"] + " course successfully"
        x = img.width//2 - len(course) * 11
        draw.text(xy=(x, 850), text=course, fill=(0, 0, 0), font=font)

        img.save('generated_certificate.pdf')

        filename = "generated_certificate.pdf"  # In same directory as script

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)

    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

@csrf_exempt
def imgtotext(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse("landing"))

    global count
    count += 1
    rapidAPIkeys = [rapidAPIkey]+[rapidAPIkey1]+[rapidAPIkey2]
    # print("count : " + str(count) + " key : " + str(keys[count%3]))
    data = json.load(request)
    imageURL = data['imageURL']

    url = "https://google-ai-vision.p.rapidapi.com/cloudVision/imageToText"

    payload = '''{
				"source":"''' + imageURL + '''",
				"sourceType":"url"
			}'''

    headers = {
        'content-type': "application/json",
        'x-rapidapi-key': rapidAPIkeys[count%3],
        'x-rapidapi-host': "google-ai-vision.p.rapidapi.com"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    try:
        return JsonResponse({"status": "success", "text": response.json()['text']})
    except:
        return JsonResponse({"status": "fail", "text": response.json()['message']})        