from django.urls import path

from . import views

urlpatterns = [
    path('class/', views.ClassroomAPIView.as_view()),
    path('home/', views.HomeAPIView.as_view()),
    path('grade/', views.GradeAPIView.as_view()),
    path('join/', views.JoinAPIView.as_view()),
    path('joinclass/', views.JoinClassAPIView.as_view()),
    path('upload/', views.UploadAPIView.as_view()),
    path('assignment/', views.AssignmentAPIView.as_view()),
    path('register/', views.RegisterAPIView.as_view()),
]