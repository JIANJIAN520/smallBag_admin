from django.urls import path
from . import views


urlpatterns = [
    path('teacher', views.teacher, name='teacher'),
    path('teacher/<int:teacher_id>/details/', views.getTeacherById, name='getTeacherById'),
    path('course', views.course, name='course'),
    path('course/<int:course_id>/detail/', views.courseDetail, name='courseDetail'),
    path('course/<int:course_id>/comment/', views.courseComment, name='courseComment'),
    path('course/<int:course_id>/like/', views.getLikes, name='getLikes'),   
    path('course/name', views.getByName, name='getByName'),
    path('course/<int:course_id>/add/comment', views.addComment, name='addComment'),
    path('course/<int:course_id>/update/like/', views.updateLike, name='updateLike'),
    path('course/<int:course_id>/detail/<int:chapter_id>/problem/', views.getProblems, name='getProblems'),
    path('user/course', views.getUserAndCourse, name='getUserAndCourse'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
]