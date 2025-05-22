from django.db import models
from users.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses') #on_delete=models.CASCADE – müəllim silinərsə, ona aid kurslar da silinir
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_embed_url(self):
        if "watch?v=" in self.video_url:
            return self.video_url.replace("watch?v=", "embed/")
        elif "youtu.be/" in self.video_url:
            video_id = self.video_url.split('/')[-1]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.video_url  



class Enrollment(models.Model):
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # eyni tələbə eyni kursa bir dəfə qoşula bilər

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"

class Exam(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices' 
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)




class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Doğru' if self.is_correct else 'Yanlış'})"
