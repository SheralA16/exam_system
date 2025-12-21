from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    # Cursos
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),

    # Exámenes
    path('courses/<int:course_id>/exams/', views.exam_list, name='exam_list'),
    path('courses/<int:course_id>/exams/create/', views.exam_create, name='exam_create'),
    path('exams/<int:pk>/edit/', views.exam_edit, name='exam_edit'),
    path('exams/<int:pk>/delete/', views.exam_delete, name='exam_delete'),

    # Preguntas y Respuestas
    path('exams/<int:exam_id>/questions/', views.question_manage, name='question_manage'),
    path('exams/<int:exam_id>/questions/create/', views.question_create, name='question_create'),
    path('questions/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('questions/<int:pk>/delete/', views.question_delete, name='question_delete'),

    # Vistas de Estudiantes
    path('student/course/<int:course_id>/exams/', views.student_course_exams, name='student_course_exams'),
    path('student/exam/<int:exam_id>/take/', views.student_take_exam, name='student_take_exam'),
    path('student/exam/<int:exam_id>/pdf/', views.student_view_pdf, name='student_view_pdf'),
    path('student/result/<int:exam_result_id>/', views.student_exam_result, name='student_exam_result'),
]
