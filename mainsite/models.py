from django.db import models
from django.contrib.auth.models import AbstractUser


class Course(models.Model):
    course_title = models.CharField(max_length=50)
    course_description = models.CharField(max_length=200)
    language = models.CharField(
        max_length=10,
        choices=[
            ('all', 'all'),
            ('cpp17', 'cpp17'),
            ('python3', 'python3'),
            ('nodejs', 'nodejs'),
            ('java', 'java'),
        ],
        default='all'
    )

    def __str__(self):
        return self.course_title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lesson_title = models.CharField(max_length=100)
    lesson_description = models.TextField(null=True)

    def __str__(self):
        return self.lesson_title


class User(AbstractUser):
    user_summary = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(max_length=50, blank=True)
    twitter_url = models.URLField(max_length=50, blank=True)
    github_url = models.URLField(max_length=50, blank=True)
    completed_lessons = models.ManyToManyField(
        Lesson, blank=True, related_name="users_completed")


class TestCase(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    input = models.TextField(blank=True)
    output = models.TextField()

    def __str__(self):
        return "Output: " + self.output
