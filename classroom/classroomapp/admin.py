from django.contrib import admin

from .models import (
    Classroom, 
    Student, Teacher, 
    Assignment, Submission, SubmitFile
)

class TeacherInline(admin.TabularInline):
    model = Teacher

class StudentInline(admin.TabularInline):
    model = Student
class ClassroomAdmin(admin.ModelAdmin):
    inlines = [
        TeacherInline,
        StudentInline,
    ]
    list_display = ['name', 'student_code', 'teacher_code']

class SubmissionInline(admin.TabularInline):
    model = Submission
class AssignmentAdmin(admin.ModelAdmin):
    inlines = [
        SubmissionInline,
    ]


class SubmitFileInline(admin.TabularInline):
    model = SubmitFile

class SubmissionAdmin(admin.ModelAdmin):
    # list_display = ['name', 'assignment', 'student', 'grade']
    inlines = [
        SubmitFileInline
    ]

admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(SubmitFile)
