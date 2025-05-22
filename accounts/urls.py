#istifadecinin brauzerde daxil etdiyi URL-ləri müvafiq view-lara yönləndirmək üçün URL konfiqurasiyası
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', login_required(views.dashboard_view, login_url='login'), name='dashboard'),
    path('enroll/<int:course_id>/', login_required(views.enroll_course, login_url='login'), name='enroll_course'),
    path('add-course/', login_required(views.add_course, login_url='login'), name='add_course'),
    path('course/<int:course_id>/add-exam/', login_required(views.add_exam_view, login_url='login'), name='add_exam'),
    path('exam/<int:exam_id>/add-question/', login_required(views.add_question_view, login_url='login'), name='add_question'),
    path('exam/<int:exam_id>/take/', login_required(views.take_exam_view, login_url='login'), name='take_exam'),
    path('exam/<int:exam_id>/certificate/', login_required(views.generate_certificate, login_url='login'), name='generate_certificate'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
]
