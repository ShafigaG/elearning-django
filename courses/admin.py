from django.contrib import admin
from .models import Course, Enrollment, Exam, Question, Answer

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Answer)
