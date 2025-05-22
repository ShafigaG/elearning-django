# daxil olan http sorgusuna gore neyin gosterileceyini mueyyen edir
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST

from django.contrib.auth import get_user_model
User = get_user_model()

from courses.models import Choice, Course, Enrollment, Exam, Question


def home_view(request):
    return render(request, 'accounts/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Yanlış istifadəçi adı və ya parol'})

    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'accounts/login.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        user = User.objects.create_user(username=username, password=password, role=role)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'accounts/signup.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def is_teacher(user):
    return user.role == 'teacher'


@login_required(login_url='login')
def dashboard_view(request):
    if request.user.role == 'student':
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        all_courses = Course.objects.all()
        enrolled_course_ids = enrollments.values_list('course_id', flat=True) #flat=True sade siyahi
        
        return render(request, 'accounts/dashboard_student.html', {
            'enrollments': enrollments,
            'all_courses': all_courses,
            'enrolled_course_ids': enrolled_course_ids,
        })

    elif request.user.role == 'teacher':
        courses = Course.objects.filter(teacher=request.user).prefetch_related('exam_set') #kurslarla bagli examleri evvelceden cekir
        return render(request, 'accounts/dashboard_teacher.html', {
            'courses': courses
        })

    elif request.user.role == 'admin':
        users = User.objects.all()
        enrollments = Enrollment.objects.all()
        return render(request, 'accounts/dashboard_admin.html', {
            'users': users,
            'enrollments': enrollments
        })

    return HttpResponse("İcazəsiz giriş", status=403)


@user_passes_test(is_teacher)
@login_required
def add_course(request):
    if request.method != 'POST':
        return HttpResponse("Yalnız POST sorğuları qəbul edilir.", status=405)

    title = request.POST['title']
    description = request.POST['description']
    video_url = request.POST.get('video_url', '')  

    Course.objects.create(
        title=title,
        description=description,
        teacher=request.user,
        video_url=video_url if video_url else None
    )
    return redirect('dashboard')



@login_required
def enroll_course(request, course_id):
    if request.user.role != 'student':
        return redirect('dashboard')

    course = get_object_or_404(Course, id=course_id)
    Enrollment.objects.get_or_create(student=request.user, course=course)
    return redirect('dashboard')


@user_passes_test(is_teacher)
@login_required
def add_exam_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        exam = Exam.objects.create(course=course, title=title, description=description)
        return redirect('add_question', exam_id=exam.id)

    return render(request, 'accounts/add_exam.html', {'course': course})


@login_required
@user_passes_test(is_teacher)
def add_question_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'POST':
        question_text = request.POST.get('question')
        choices = request.POST.getlist('choice')
        correct_index = int(request.POST.get('correct_choice'))

        if not question_text or not choices or correct_index is None:
            return HttpResponse("Çatışmayan məlumatlar var.", status=400)

        question = Question.objects.create(exam=exam, text=question_text)

        for i, choice_text in enumerate(choices):
            Choice.objects.create(
                question=question,
                text=choice_text,
                is_correct=(i == correct_index)
            )

        if 'submit_continue' in request.POST:
            return redirect('add_question', exam_id=exam.id)
        else:
            return redirect('dashboard')

    questions = exam.question_set.prefetch_related('choices')
    return render(request, 'accounts/add_question.html', {
        'exam': exam,
        'questions': questions
    })

@login_required
def take_exam_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'POST':
        total = 0
        correct = 0

        for question in exam.question_set.all():
            selected_choice_id = request.POST.get(str(question.id))
            if selected_choice_id:
                try:
                    selected_choice = Choice.objects.get(id=int(selected_choice_id))
                except Choice.DoesNotExist:
                    continue
                if selected_choice.is_correct:
                    correct += 1
                total += 1

        return render(request, 'accounts/exam_result.html', {
            'correct': correct,
            'total': total,
            'exam': exam
        })

    return render(request, 'accounts/take_exam.html', {'exam': exam})

from django.http import FileResponse
from reportlab.pdfgen import canvas
from io import BytesIO

from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from io import BytesIO
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def generate_certificate(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    student = request.user

    # PDF üçün müvəqqəti yaddaş buferi
    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    p.setFont("Helvetica-Bold", 26)
    p.drawCentredString(width / 2, height - 4 * cm, "Nailiyyet Sertifikati")

    p.setFont("Helvetica", 16)
    p.drawCentredString(width / 2, height - 6 * cm, f"{student.username} imtahani ugurla basha vurdu.")
    p.drawCentredString(width / 2, height - 7 * cm, f"Imtahan: {exam.title}")
    p.drawCentredString(width / 2, height - 8 * cm, "Tam bal toplayaraq bu sertifikati qazandi.")
    p.drawCentredString(width / 2, height - 9 * cm, "Tebrik edirik!")

    # date elave etmek
    date_str = datetime.now().strftime("%d.%m.%Y")
    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(width / 2, height - 11 * cm, f"Tarix: {date_str}")

    # teshkilat adi ve rehberi
    p.setFont("Helvetica", 12)
    p.drawString(3 * cm, 5 * cm, "_____________________")
    p.drawString(3 * cm, 4.3 * cm, "Teshkilat Adi")

    p.drawString(width - 8 * cm, 5 * cm, "_____________________")
    p.drawString(width - 8 * cm, 4.3 * cm, "Teshkilat Rehberi")

    # etrafina cercive cekmek
    p.setLineWidth(4)
    p.rect(1 * cm, 1 * cm, width - 2 * cm, height - 2 * cm)

    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='sertifikat.pdf')


def dashboard_student_view(request):
    user = request.user
    enrollments = Enrollment.objects.filter(student=user)
    all_courses = Course.objects.all()
    
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    
    context = {
        'enrollments': enrollments,
        'all_courses': all_courses,
        'enrolled_course_ids': enrolled_course_ids,
    }
    return render(request, 'accounts/dashboard_student.html', context)

def course_list_view(request):
    user = request.user
    courses = Course.objects.all() 
    enrolled_courses = []
    if user.is_authenticated:
        enrolled_courses = Enrollment.objects.filter(student=user).values_list('course_id', flat=True)
    
    context = {
        'courses': courses,
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'accounts/course_list.html', context)

def my_courses_view(request):
    user = request.user
    enrolled_courses = Course.objects.filter(enrollments__student=user)
    
    context = {
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'accounts/my_courses.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'accounts/course_detail.html', {'course': course})
