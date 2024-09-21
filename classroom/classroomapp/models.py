from django.db import models

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

class Classroom(models.Model):
    """
    many to many - User (student & teacher)
    one to many - Assignment
    """
    name = models.CharField(max_length=100, default='class_', null=True)
    code = models.CharField(max_length=15, null=True, unique=True)

    def __str__(self):
        return str(self.pk) + ' ' + self.name

from django.contrib.auth.models import User

def newstr(self):
    return str(self.id) + ' ' + self.username

User.__str__ = newstr
class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    def __str__(self):
        return 'class: ' + str(self.classroom.id) + '-' + self.classroom.name + ' ' + str(self.user.id) + '-' + self.user.username
    
class Teacher(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    
    def __str__(self):
        return 'teacher: user of ' + self.user.username
    
class Assignment(models.Model):
    name = models.CharField(max_length=100)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, null=True)
    description = models.TextField()
    deadline = models.DateTimeField(null=True)
    
    def __str__(self):
        return self.classroom.name + ' - ' + str(self.pk) + ': ' + self.name


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    grade = models.IntegerField(default=0)

    def __str__(self):
        return self.assignment.classroom.name + ' ' + self.assignment.name + ': ' + self.student.user.username

class SubmitFile(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    file = models.FileField(null=True)

    def __str__(self):
        return str(self.pk) + ': ' + self.submission.assignment.classroom.name + ' ' + self.submission.assignment.name + ': ' + self.submission.student.user.username + ': ' + self.file.name









"""many to one test class"""
class Reporter(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Article(models.Model):
    headline = models.CharField(max_length=100)
    pub_date = models.DateField()
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)

    def __str__(self):
        return self.headline

    class Meta:
        ordering = ["headline"]