from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('join/', views.join),
    path('invite/', views.invite),
    # path('createclass/', views.create_class),
    # path('deleteclass/', views.delete_class),
    # path('updateclass/', views.update_class),
    path('class/', views.ClassroomAPIView.as_view()),
    path('home/', views.HomeAPIView.as_view()),
    path('grade/', views.GradeAPIView.as_view()),
    path('join/', views.JoinAPIView.as_view()),
    path('joinclass/', views.JoinClassAPIView.as_view()),

    path('deleteclass/', views.delete_class),
    path('updateclass/', views.update_class),
    
    path('class/<classid>', views.get_class),
    path('createjoincode/', views.create_join_code),
    path('removejoincode/', views.remove_join_code),
    path('createassignment/', views.create_assignment),

    path('loginview/', views.LoginView.as_view()),


    path('upload/', views.UploadAPIView.as_view()),

    path('assignment/', views.AssignmentAPIView.as_view()),

    path('rest_login/', views.ExampleView.as_view()),
    path('register/', views.RegisterAPIView.as_view()),
]