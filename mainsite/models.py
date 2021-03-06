from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    user_summary = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(max_length=50, blank=True)
    twitter_url = models.URLField(max_length=50, blank=True)
    github_url = models.URLField(max_length=50, blank=True)


class Course(models.Model):
    course_title = models.CharField(max_length=50)
    course_description = models.CharField(max_length=200)

    def __str__(self):
        return self.course_title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson_title = models.CharField(max_length=100)

    def __str__(self):
        return self.lesson_title
