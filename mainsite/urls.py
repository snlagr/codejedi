from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("courses", views.courses, name="courses"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("profile", views.profile_edit, name="edit_profile"),
    path("profile/<str:username>", views.profile_view, name="view_profile"),
    path("courses/<int:course_id>", views.course_view, name="view_course"),
    path("lesson/<int:lesson_id>", views.lesson_view, name="view_lesson")
]
