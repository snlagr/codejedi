from django.contrib import admin
from .models import User, Course, Lesson, TestCase


class TestCaseInline(admin.StackedInline):
    model = TestCase
    extra = 1


class LessonAdmin(admin.ModelAdmin):
    inlines = [TestCaseInline]


class UserAdmin(admin.ModelAdmin):
    filter_horizontal = ("completed_lessons",)


admin.site.register(User, UserAdmin)
admin.site.register(Course)
admin.site.register(Lesson, LessonAdmin)
