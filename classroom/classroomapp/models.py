from django.db import models

class Classroom(models.Model):
    """
    many to many - User (student & teacher)
    one to many - Assignment
    """
    name = models.CharField(max_length=100, default='class_', null=True)
    student_code = models.CharField(max_length=15, null=True, unique=True)
    teacher_code = models.CharField(max_length=15, null=True, unique=True)

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
        return str(self.classroom.id) + '-' + self.classroom.name + ' ' + str(self.user.id) + '-' + self.user.username
    
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
        return str(self.classroom.id) + '-' + self.classroom.name + ' ' + str(self.pk) + '-' + self.name


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    grade = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id) + ' ' + str(self.assignment.classroom.id) + '-' + self.assignment.classroom.name + ' ' + str(self.assignment.id) + '-' + self.assignment.name + ' ' + self.student.user.username

class SubmitFile(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    file = models.FileField(null=True)

    def __str__(self):
        return str(self.pk) + ' ' + str(self.submission.assignment.classroom.pk) + '-' + self.submission.assignment.classroom.name + ' ' + str(self.submission.assignment.pk) + '-' + self.submission.assignment.name + ' ' + str(self.submission.student.user.id) + '-' + self.submission.student.user.username + ' ' + self.file.name
    