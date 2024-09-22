import string
import random

import traceback

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.views import View

from .models import (
    User, Teacher, Student,
    Classroom, Assignment, Submission, SubmitFile
)

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import SubmitFileSerializer

from datetime import datetime
from django.utils import timezone

from django.contrib.auth import models
from django.contrib.auth.hashers import make_password

class RegisterAPIView(APIView):
    def post(self, request):
        user = models.User(username=request.data['username'], password=make_password(request.data['password']))
        user.save()
        return JsonResponse({'msg': 'Account created'})

class HomeAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """gets all class related to this user"""
        user = User.objects.get(id=request.user.id)
        classrooms = [student.classroom for student in user.student_set.all()] + [teacher.classroom for teacher in user.teacher_set.all()]

        classrooms = [
            {
                'id':classroom.id,
                'name':classroom.name
            } for classroom in classrooms
        ]
        
        return JsonResponse({'classrooms': classrooms})

class JoinClassAPIView(APIView):
    def post(self, request):
        user = User.objects.get(id=request.user.id)

        # get classroom
        classroom = Classroom.objects.filter(id=request.data['classroom_id'])
        if not classroom:
            return JsonResponse({'msg': 'Nonexistent classroom'})

        if not classroom.first().student_code:
            return JsonResponse({'msg': classroom.first().name + ' not accepting students'})
        
        if not classroom.first().teacher_code:
            return JsonResponse({'msg': classroom.first().name + ' not accepting teachers'})
        
        # check for duplicate
        student = classroom.first().student_set.filter(user__id=user.id)
        teacher = classroom.first().teacher_set.filter(user__id=user.id)
        if student or teacher:
            s = ' as a teacher' if teacher else ' as a student'
            return JsonResponse({'msg': 'Already joined ' + classroom.first().name + s})
        
        try:
            if classroom.first().teacher_code == request.data['teacher_code']:
                user.teacher_set.create(classroom=classroom.first())
                return JsonResponse({'msg': 'Joined ' + classroom.first().name + ' as a teacher'})
        except Exception as _:
            print('There is no teacher code')

        # validate join code
        if not classroom.first().student_code == request.data['student_code']:
            return JsonResponse({'msg': 'Code don\'t match'})
        
        user.student_set.create(classroom=classroom.first())
        return JsonResponse({'msg': 'Joined ' + classroom.first().name + ' as a student'})
    
    def delete(self, request):
        """leave class function for student and teacher
        
        if the last teacher leaves, the class will also be deleted
        """

        # get classroom
        classroom = Classroom.objects.filter(id=request.data['classroom_id'])
        if not classroom:
            return JsonResponse({'msg': 'Nonexistent classroom'})

        # get user role in classroom
        student = classroom.first().student_set.filter(user__id=request.user.id)
        teacher = classroom.first().teacher_set.filter(user_id=request.user.id)

        if not student or teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        
        if teacher:
            # check if its the last teacher
            if classroom.first().teacher_set.all().length < 1:
                classroom.first().delete()
                return JsonResponse({'msg': classroom.first().name + ' deleted'})
            
            teacher.first().delete()
            return JsonResponse({'msg': 'Left ' + classroom.first().name})
        
        student.first().delete()
        
        return JsonResponse({'msg': 'Left ' + classroom.first().name})


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_id(classroom):
    id = id_generator()
    if classroom.student_code == id:
        get_id(classroom)
    return id

class JoinAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """get join code for teacher"""
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexisting classroom'})
        
        classroom = teacher.first().classroom
        return JsonResponse({'classroom_name': classroom.name, 'classroom_student_code': classroom.student_code, 'classroom_teacher_code': classroom.teacher_code})

    def post(self, request):
        """create/recreate join code by teacher"""
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})

        teacher = teacher.first()
        try:
            teacher.classroom.teacher_code = request.data['teacher_code']
            try:
                teacher.classroom.save()
            except Exception as _:
                return JsonResponse({'msg': 'Teacher code has been taken'})
            
            return JsonResponse({
                'msg': 'Classroom teacher join code is created', 
                'teacher_code': teacher.classroom.teacher_code
            })
        except Exception as _:
            print('There is no teacher code')

        i = 0
        while True:
            codes = [classroom.student_code for classroom in Classroom.objects.all()]
            new_code = get_id(teacher.classroom)
            if new_code not in codes:
                teacher.classroom.student_code = new_code
                teacher.classroom.save()
                break
            i += 1
            if i == 10:
                return JsonResponse({'msg': 'Try again'})
        
        return JsonResponse({
            'msg': 'Classroom join code create', 
            'student_code': teacher.classroom.student_code, 
        })

    def delete(self, request):
        """remove join code by teacher, disables the use of the code"""
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        teacher = teacher.first()

        role = request.data['role']
        if role == 'teacher':
            teacher.classroom.teacher_code = None
            teacher.classroom.save()
            return JsonResponse({'msg': 'Classroom teacher code deleted'})
        elif role == 'student':
            teacher.classroom.save()
            teacher.classroom.student_code = None
            return JsonResponse({'msg': 'Classroom student code deleted'})

        return JsonResponse({'msg': 'Use \'teacher\' or \'student\' as role'})

class ClassroomAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """gets a class selected by user"""
        role = Student.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not role:
            role = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
            
            if not role:
                return JsonResponse({'msg': 'Nonexistent classroom'})

        # gets the class
        classroom = role.first().classroom
        # gets the assingments of the class
        assignments = classroom.assignment_set.all()
        data = [{
            'id': assignment.id, 'name': assignment.name, 'description': assignment.description
        } for assignment in assignments]
        return JsonResponse({'data': data})

    def post(self, request, *args, **kwargs):
        print(request.data)
        # print(int(request.data['user_id']))
        # user1 = User.objects.get(id=request.data['user_id'])
        user = User.objects.get(id=request.user.pk)

        classroom = Classroom(name=request.data['name'])
        classroom.save()
        teacher1 = Teacher(user=user, classroom=classroom)
        teacher1.save()
        # classroom.teachers.add(teacher1)
        return JsonResponse({'msg': 'Class created'})

    def put(self, request, *args, **kwargs):
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})

        classroom = teacher.first().classroom.filter(id=request.data['classroom_id'])
        if not classroom:
            return JsonResponse({'msg': 'Nonexistent classroom'})

        classroom.name = request.data['name']
        classroom.save()
        return JsonResponse({'msg': 'Class updated'})

    def delete(self, request, *args, **kwargs):
        """delete a classroom"""
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        
        try:
            teacher.first().classroom.get(id=request.data['classroom_id']).delete()
        except Exception as _:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        return JsonResponse({'msg': 'Class deleted'})

class AssignmentAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        role = Student.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not role:
            role = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])

            if not role:
                return JsonResponse({'msg': 'Nonexistent classroom'})
            
        classroom = role.first().classroom
        
        assignment = classroom.assignment_set.filter(id=request.data['assignment_id'])
        if not assignment:
            return JsonResponse({'msg': 'Nonexistent assignment'})
        assignment = assignment.first()

        return JsonResponse({
            'name': assignment.name,
            'description': assignment.description
        })
    
    def post(self, request, *args, **kwargs):
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        
        assignment = Assignment(
            name=request.data['name'], 
            classroom=teacher.first().classroom, 
            description=request.data['description']
        )

        try:
            assignment.deadline = datetime.strptime(request.data['assignment_deadline'], '%Y-%m-%d %H:%M')
        except Exception as _:
            print('There is no deadline')

        assignment.save()
        return JsonResponse({'msg': 'Assignment created'})
    
    def put(self, request, *args, **kwargs):
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        
        assignment = teacher.first().classroom.assignment_set.get(id=request.data['assignment_id'])
        assignment.name = request.data['name']
        assignment.description = request.data['description']

        try:
            assignment.deadline = datetime.strptime(request.data['assignment_deadline'], '%Y-%m-%d %H:%M')
        except Exception as _:
            print('There is no assignment deadline')

        assignment.save()
        return JsonResponse({'msg': 'Assignment updated'})

    def delete(self, request, *args, **kwargs):
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        
        try:
            teacher.first().classroom.assignment_set.get(id=request.data['assignment_id']).delete()
        except Exception as _:
            return JsonResponse({'msg': 'Nonexistent assignment'})
        
        return JsonResponse({'msg': 'Assignment deleted'})

class UploadAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        return files related to a submission from an assignment from a user in a classroom

        User needs to be a student in this classroom
        
        """
        student = Student.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not student:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        student = student.first()

        assignment = student.classroom.assignment_set.get(id=request.data['assignment_id'])
        submission = assignment.submission_set.filter(student__id=student.id, assignment__id=assignment.id)
        if not submission:
            return JsonResponse({'msg': 'There\'s no submission to this assignment'})
        submission = submission.first()

        submit_files = submission.submitfile_set.all()
        if not submit_files:
            return JsonResponse({'msg': 'There\'s no file uploaded for this submission'})

        context = {'request': request}
        serializer = SubmitFileSerializer(submit_files, context=context, many=True)
        
        print(serializer.data)
        return Response(serializer.data)
        # return JsonResponse({'data': [ins.file for ins in submit_files]})

    def post(self, request, *args, **kwarsg):
        """
        check if there's already a submission
         use assignment id, (user id, classroom id) -> student, 
        create a submission if there isn't
        create submit file instance

        """
        student = Student.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not student:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        student = student.first()

        assignment = student.classroom.assignment_set.get(id=request.data['assignment_id'])

        if assignment.deadline:
            print(assignment.deadline)
            if timezone.now() > assignment.deadline:
                return JsonResponse({'msg': 'Past deadline'})
            
        submission = assignment.submission_set.filter(student__id=student.id, assignment__id=assignment.id)
        if not submission:
            submission = Submission(assignment=assignment, student=student)
            submission.save()
        else:
            submission = submission.first()

        file = SubmitFile(submission=submission, file=request.data['file'])
        file.save()

        return JsonResponse({'msg': 'File uploaded'})
    
    def delete(self, request, *args, **kwargs):
        """
        delete a submitfile instance from a submission
        """
        student = Student.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not student:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        student = student.first()

        assignment = student.classroom.assignment_set.get(id=request.data['assignment_id'])

        if assignment.deadline:
            if timezone.now() > assignment.deadline:
                return JsonResponse({'msg': 'Past deadline'})
        
        submission = assignment.submission_set.filter(student__id=student.id, assignment__id=assignment.id)
        if not submission:
            return JsonResponse({'msg': 'There\' no submission to this assignment'})
        submission = submission.first()

        try:
            submitfile = submission.submitfile_set.get(id=request.data['submitfile_id'])
            submitfile.file.delete()
            submitfile.delete()
        except Exception as _:
            return JsonResponse({'msg': 'Nonexisting submit file'})
        return JsonResponse({'msg': 'File deleted'})
    
"""Needs teacher role"""
class GradeAPIView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        get all submissions within a class for an assignment
        """
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        
        assignment = teacher.first().classroom.assignment_set.filter(id=request.data['assignment_id'])
        if not assignment:
            return JsonResponse({'msg': 'Nonexistent assignment'})

        submissions = [submission for submission in assignment.first().submission_set.all()]

        context = {
            'request': request
        }
        submissions = [
            {
                'id': submission.id,
                'student': submission.student.user.username,
                'grade': submission.grade,
                'submitfiles': SubmitFileSerializer(submission.submitfile_set.all(), many=True, context=context).data
            } 
            for submission in submissions
        ]
        return JsonResponse({'submissions': submissions})
            
    def post(self, request):
        """
        grade a submission for an assignment within a class
        """
        teacher = Teacher.objects.filter(user__id=request.user.id, classroom__id=request.data['classroom_id'])
        if not teacher:
            return JsonResponse({'msg': 'Nonexistent classroom'})
        
        assignment = teacher.first().classroom.assignment_set.filter(id=request.data['assignment_id'])
        if not assignment:
            return JsonResponse({'msg': 'Nonexistent assignment'})
            
        submission = assignment.first().submission_set.filter(id=request.data['submission_id'])
        if not submission:
            return JsonResponse({'msg': 'Nonexistent submission'})
    
        submission = submission.first()
        submission.grade = request.data['assignment_grade']
        submission.save()
        return JsonResponse({'msg': 'Submission graded'})
