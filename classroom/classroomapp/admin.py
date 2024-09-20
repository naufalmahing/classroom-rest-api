from django.contrib import admin

from .models import (
    Question, Choice, 
    Classroom, 
    Student, Teacher, User, 
    Assignment, Submission, SubmitFile
)

from .models import Reporter, Article

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Classroom)
admin.site.register(Student)
admin.site.register(Teacher)
# admin.site.register(User)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(SubmitFile)



admin.site.register(Reporter)
admin.site.register(Article)